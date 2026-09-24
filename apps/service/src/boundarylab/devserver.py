from __future__ import annotations

import argparse
import asyncio
import os
import secrets
from pathlib import Path

import uvicorn

from .app import ROOT, Settings, create_app, default_targets
from .fixture import Variant, create_fixture_app


async def serve(settings: Settings) -> None:
    applications = [
        (create_app(settings), 8080),
        (create_fixture_app(Variant.VULNERABLE), 9011),
        (create_fixture_app(Variant.OWNER_ONLY), 9012),
        (create_fixture_app(Variant.FIXED), 9013),
    ]
    servers: list[uvicorn.Server] = []
    for application, port in applications:
        server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=port, log_level="warning"))
        server.install_signal_handlers = lambda: None
        servers.append(server)
    print("BoundaryLab local workbench: http://127.0.0.1:8080")
    print("Three synthetic targets: 127.0.0.1 ports 9011–9013")
    print("Bootstrap secret (local demo only):", settings.bootstrap_secret)
    try:
        await asyncio.gather(*(server.serve() for server in servers))
    finally:
        for server in servers:
            server.should_exit = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Start BoundaryLab control plane and three local synthetic targets")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "var")
    parser.add_argument("--bootstrap-secret", default=None)
    args = parser.parse_args()
    secret = args.bootstrap_secret or secrets.token_urlsafe(18)
    if len(secret) < 16:
        parser.error("--bootstrap-secret must be at least 16 characters")
    settings = Settings(
        database_path=args.data_dir / "boundarylab.db",
        bootstrap_secret=secret,
        targets=default_targets(),
        openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
        ai_model=os.environ.get("BOUNDARYLAB_AI_MODEL", "gpt-6-astra"),
    )
    asyncio.run(serve(settings))


if __name__ == "__main__":
    main()
