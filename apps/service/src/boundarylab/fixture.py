from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict


class Variant(StrEnum):
    VULNERABLE = "vulnerable"
    OWNER_ONLY = "owner-only"
    FIXED = "fixed"


TOKENS = {
    "token-alice": ("alice", "A"),
    "token-bob": ("bob", "A"),
    "token-mallory": ("mallory", "B"),
}
LAB_TOKEN = "lab-factory-token"


@dataclass(slots=True)
class Invoice:
    id: str
    namespace: str
    owner_id: str
    tenant_id: str
    content_marker: str
    internal_bank_ref: str
    shares: set[str] = field(default_factory=set)


@dataclass(slots=True)
class Export:
    id: str
    namespace: str
    invoice_id: str
    creator_id: str
    ready_at: float


class FixtureStore:
    def __init__(self, variant: Variant, export_delay_ms: int = 10):
        self.variant = variant
        self.export_delay_ms = export_delay_ms
        self.invoices: dict[str, Invoice] = {}
        self.exports: dict[str, Export] = {}
        self.namespaces: set[str] = set()

    def create_namespace(self) -> dict:
        namespace = uuid.uuid4().hex[:12]
        private_id = f"{namespace}-private"
        shared_id = f"{namespace}-shared"
        self.namespaces.add(namespace)
        self.invoices[private_id] = Invoice(private_id, namespace, "alice", "A", f"CANARY-{namespace}-PRIVATE", f"BANK-{namespace}-PRIVATE")
        self.invoices[shared_id] = Invoice(shared_id, namespace, "alice", "A", f"CANARY-{namespace}-SHARED", f"BANK-{namespace}-SHARED")
        return {
            "namespace": namespace,
            "identity_tokens": {"alice": "token-alice", "bob": "token-bob", "mallory": "token-mallory"},
            "objects": {"private_invoice": private_id, "shared_invoice": shared_id},
            "markers": {"private_invoice": self.invoices[private_id].content_marker, "shared_invoice": self.invoices[shared_id].content_marker},
        }

    def cleanup(self, namespace: str) -> None:
        if namespace not in self.namespaces:
            return
        invoice_ids = {key for key, value in self.invoices.items() if value.namespace == namespace}
        self.invoices = {key: value for key, value in self.invoices.items() if key not in invoice_ids}
        self.exports = {key: value for key, value in self.exports.items() if value.namespace != namespace}
        self.namespaces.remove(namespace)


class ShareBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: str


def create_fixture_app(variant: Variant | str, *, export_delay_ms: int = 10) -> FastAPI:
    selected = Variant(variant)
    store = FixtureStore(selected, export_delay_ms)
    app = FastAPI(title="BoundaryLab synthetic invoice fixture", version="1.0.0")
    app.state.store = store

    def identity(authorization: str | None = Header(default=None)) -> tuple[str, str]:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail={"code": "AUTH_REQUIRED"})
        value = TOKENS.get(authorization.removeprefix("Bearer "))
        if not value:
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN"})
        return value

    def lab_identity(authorization: str | None = Header(default=None)) -> None:
        if authorization != f"Bearer {LAB_TOKEN}":
            raise HTTPException(status_code=403, detail={"code": "LAB_SCOPE_REQUIRED"})

    def invoice_or_404(invoice_id: str) -> Invoice:
        if invoice_id not in store.invoices:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        return store.invoices[invoice_id]

    def can_read(invoice: Invoice, subject: str) -> bool:
        if selected == Variant.OWNER_ONLY:
            return invoice.owner_id == subject
        return invoice.owner_id == subject or subject in invoice.shares

    @app.get("/healthz", operation_id="health")
    async def health():
        return {"build_id": f"invoice-{selected.value}", "fixture_semantics_version": "invoice-fixtures-v1"}

    @app.get("/v1/me", operation_id="getMe")
    async def get_me(caller=Depends(identity)):
        return {"subject_id": caller[0], "tenant_id": caller[1]}

    @app.get("/v1/invoices/{invoice_id}/preview", operation_id="getInvoicePreview")
    async def get_preview(invoice_id: str, caller=Depends(identity)):
        invoice = invoice_or_404(invoice_id)
        if selected != Variant.VULNERABLE and invoice.owner_id != caller[0]:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        return {"id": invoice.id, "content_marker": invoice.content_marker}

    @app.get("/v1/invoices/{invoice_id}", operation_id="getInvoice")
    async def get_invoice(invoice_id: str, caller=Depends(identity)):
        invoice = invoice_or_404(invoice_id)
        if not can_read(invoice, caller[0]):
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        result = {"id": invoice.id, "owner_id": invoice.owner_id, "tenant_id": invoice.tenant_id, "content_marker": invoice.content_marker}
        if caller[0] == invoice.owner_id or selected == Variant.VULNERABLE:
            result["internal_bank_ref"] = invoice.internal_bank_ref
        return result

    @app.post("/v1/invoices/{invoice_id}/shares", status_code=201, operation_id="grantShare")
    async def grant_share(invoice_id: str, body: ShareBody, caller=Depends(identity)):
        invoice = invoice_or_404(invoice_id)
        if caller[0] != invoice.owner_id:
            raise HTTPException(status_code=403, detail={"code": "OWNER_REQUIRED"})
        invoice.shares.add(body.subject_id)
        return {"subject_id": body.subject_id, "active": True}

    @app.delete("/v1/invoices/{invoice_id}/shares/{subject_id}", status_code=204, operation_id="revokeShare")
    async def revoke_share(invoice_id: str, subject_id: str, caller=Depends(identity)):
        invoice = invoice_or_404(invoice_id)
        if caller[0] != invoice.owner_id:
            raise HTTPException(status_code=403, detail={"code": "OWNER_REQUIRED"})
        invoice.shares.discard(subject_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.post("/v1/invoices/{invoice_id}/exports", status_code=202, operation_id="queueExport")
    async def queue_export(invoice_id: str, caller=Depends(identity)):
        invoice = invoice_or_404(invoice_id)
        if not can_read(invoice, caller[0]):
            raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED"})
        export_id = f"{invoice.namespace}-export-{uuid.uuid4().hex[:8]}"
        store.exports[export_id] = Export(export_id, invoice.namespace, invoice.id, caller[0], time.monotonic() + store.export_delay_ms / 1000)
        return {"id": export_id, "invoice_id": invoice.id, "creator_id": caller[0], "state": "queued"}

    @app.get("/v1/exports/{export_id}", operation_id="getExport")
    async def get_export(export_id: str, caller=Depends(identity)):
        export = store.exports.get(export_id)
        if not export:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        invoice = invoice_or_404(export.invoice_id)
        if not (invoice.owner_id == caller[0] or export.creator_id == caller[0]):
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        state_value = "ready" if time.monotonic() >= export.ready_at else "queued"
        return {"id": export.id, "invoice_id": export.invoice_id, "creator_id": export.creator_id, "state": state_value}

    @app.get("/v1/exports/{export_id}/content", operation_id="getExportContent")
    async def get_export_content(export_id: str, caller=Depends(identity)):
        export = store.exports.get(export_id)
        if not export:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
        if time.monotonic() < export.ready_at:
            raise HTTPException(status_code=409, detail={"code": "NOT_READY"})
        invoice = invoice_or_404(export.invoice_id)
        if selected == Variant.VULNERABLE:
            allowed = invoice.owner_id == caller[0] or export.creator_id == caller[0]
        else:
            allowed = can_read(invoice, caller[0])
        if not allowed:
            raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED"})
        return {"invoice_id": invoice.id, "content_marker": invoice.content_marker}

    @app.post("/__lab/fixtures", operation_id="labCreate")
    async def create_namespace(_: None = Depends(lab_identity)):
        return store.create_namespace()

    @app.delete("/__lab/fixtures/{namespace}", status_code=204, operation_id="labCleanup")
    async def cleanup_namespace(namespace: str, _: None = Depends(lab_identity)):
        store.cleanup(namespace)
        return Response(status_code=204)

    return app
