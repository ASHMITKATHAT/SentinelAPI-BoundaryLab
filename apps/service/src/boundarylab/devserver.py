from __future__ import annotations

import argparse
import asyncio
import os
import secrets
from pathlib import Path

import uvicorn

from .app import ROOT, Settings, create_app, default_targets
from .fixture import Variant, create_fixture_app


async def serve(settings: Settings, control_host: str = "127.0.0.1") -> None:
    applications = [
        (create_app(settings), control_host, 8080),
        (create_fixture_app(Variant.VULNERABLE), "127.0.0.1", 9011),
        (create_fixture_app(Variant.OWNER_ONLY), "127.0.0.1", 9012),
        (create_fixture_app(Variant.FIXED), "127.0.0.1", 9013),
    ]
    servers: list[uvicorn.Server] = []
    for application, host, port in applications:
        server = uvicorn.Server(uvicorn.Config(application, host=host, port=port, log_level="warning"))
        server.install_signal_handlers = lambda: None
        servers.append(server)
    display_host = "127.0.0.1" if control_host == "0.0.0.0" else control_host
    print(f"BoundaryLab local workbench: http://{display_host}:8080")
    print("Three synthetic targets: 127.0.0.1 ports 9011–9013")
    try:
        await asyncio.gather(*(server.serve() for server in servers))
    finally:
        for server in servers:
            server.should_exit = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Start BoundaryLab control plane and three local synthetic targets")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "var")
    parser.add_argument("--bootstrap-secret", default=None)
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    args = parser.parse_args()
    configured_secret = args.bootstrap_secret or os.environ.get("BOUNDARYLAB_BOOTSTRAP_SECRET")
    secret = configured_secret or secrets.token_urlsafe(18)
    if len(secret) < 16:
        parser.error("bootstrap secret must be at least 16 characters")
    if not configured_secret:
        print("Generated bootstrap secret (shown once):", secret)
    settings = Settings(
        database_path=args.data_dir / "boundarylab.db",
        bootstrap_secret=secret,
        targets=default_targets(),
        openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
        ai_model=os.environ.get("BOUNDARYLAB_AI_MODEL", "gpt-6-astra"),
    )
    asyncio.run(serve(settings, args.host))


if __name__ == "__main__":
    main()
