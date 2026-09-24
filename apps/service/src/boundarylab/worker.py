from __future__ import annotations

import asyncio
import logging

import httpx

from .real_scenario import AccessProbeScenario
from .repository import Repository
from .scenario import InvoiceScenario
from .serialization import report_to_dict
from .targets import TrustedTarget
from .transport import ScopedTransport, TransportLimits


log = logging.getLogger(__name__)


class RunWorker:
    def __init__(self, repository: Repository, targets: dict[str, TrustedTarget]):
        self.repository = repository
        self.targets = targets
        self._wake = asyncio.Event()
        self._stop = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._active_run_id: str | None = None
        self._active_cancel: asyncio.Event | None = None

    def start(self) -> None:
        if not self._task:
            self._task = asyncio.create_task(self._loop(), name="boundarylab-run-worker")

    async def stop(self) -> None:
        self._stop.set()
        if self._active_cancel:
            self._active_cancel.set()
        self._wake.set()
        if self._task:
            await self._task

    def notify(self) -> None:
        self._wake.set()

    def cancel(self, run_id: str) -> dict | None:
        run = self.repository.request_cancel(run_id)
        if self._active_run_id == run_id and self._active_cancel:
            self._active_cancel.set()
        self._wake.set()
        return run

    async def _loop(self) -> None:
        while not self._stop.is_set():
            run = self.repository.claim_next_run()
            if not run:
                self._wake.clear()
                try:
                    await asyncio.wait_for(self._wake.wait(), timeout=0.5)
                except TimeoutError:
                    pass
                continue
            await self._execute(run)

    async def _execute(self, run: dict) -> None:
        run_id = run["id"]
        target = self.targets.get(run["target_alias"])
        if not target or target.origin != run["target_origin"]:
            self.repository.fail_run(run_id, "failed", "trusted target configuration changed")
            return
        self._active_run_id = run_id
        self._active_cancel = asyncio.Event()
        try:
            limits = httpx.Limits(max_connections=1, max_keepalive_connections=1)
            async with httpx.AsyncClient(
                timeout=None,
                follow_redirects=False,
                trust_env=False,
                limits=limits,
                headers={"User-Agent": "BoundaryLab/0.3.1 local-runner"},
            ) as client:
                transport = ScopedTransport(
                    client,
                    base_url=target.origin,
                    limits=TransportLimits(max_requests=20, cleanup_reserve=0) if target.adapter else TransportLimits(),
                    cancel_event=self._active_cancel,
                    operations={target.adapter.operation_id: target.adapter.operation} if target.adapter else None,
                )
                if target.adapter:
                    report = await AccessProbeScenario(
                        transport,
                        target_alias=target.alias,
                        adapter=target.adapter,
                    ).run()
                else:
                    report = await InvoiceScenario(transport, target_alias=target.alias).run()
            if self._stop.is_set():
                self.repository.fail_run(run_id, "interrupted", "service stopped during run")
            elif self._active_cancel.is_set():
                self.repository.fail_run(run_id, "cancelled", "operator cancelled run; cleanup attempted")
            else:
                self.repository.complete_run(run_id, report_to_dict(report))
        except asyncio.CancelledError:
            state = "interrupted" if self._stop.is_set() else "cancelled"
            self.repository.fail_run(run_id, state, "worker task cancelled")
        except Exception as exc:
            log.exception("run %s failed", run_id)
            self.repository.fail_run(run_id, "failed", f"{type(exc).__name__}: {exc}")
        finally:
            self._active_run_id = None
            self._active_cancel = None
