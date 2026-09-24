from __future__ import annotations

import argparse
import asyncio
import os
import secrets
from pathlib import Path

import uvicorn

from .app import ROOT, Settings, create_app, default_targets
from .fixture import Variant, create_fixture_app
from .targets import load_real_targets


async def serve(settings: Settings, control_host: str = "127.0.0.1", *, with_lab_fixtures: bool = False) -> None:
    applications = [(create_app(settings), control_host, 8080)]
    if with_lab_fixtures:
        applications.extend([
            (create_fixture_app(Variant.VULNERABLE), "127.0.0.1", 9011),
            (create_fixture_app(Variant.OWNER_ONLY), "127.0.0.1", 9012),
            (create_fixture_app(Variant.FIXED), "127.0.0.1", 9013),
        ])
    servers: list[uvicorn.Server] = []
    for application, host, port in applications:
        server = uvicorn.Server(uvicorn.Config(application, host=host, port=port, log_level="warning"))
        server.install_signal_handlers = lambda: None
        servers.append(server)
    display_host = "127.0.0.1" if control_host == "0.0.0.0" else control_host
    print(f"BoundaryLab local workbench: http://{display_host}:8080")
    if with_lab_fixtures:
        print("Explicit lab mode: synthetic targets on 127.0.0.1 ports 9011–9013")
    elif settings.targets:
        print(f"Real target registry loaded: {len(settings.targets)} target(s)")
    else:
        print("No active target configured; add --target-config for real staging tests")
    try:
        await asyncio.gather(*(server.serve() for server in servers))
    finally:
        for server in servers:
            server.should_exit = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the BoundaryLab control plane")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "var")
    parser.add_argument("--bootstrap-secret", default=None)
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    parser.add_argument("--target-config", type=Path, default=None, help="reviewed real-target registry JSON")
    parser.add_argument("--with-lab-fixtures", action="store_true", help="explicitly enable the synthetic three-build lab")
    args = parser.parse_args()
    configured_secret = args.bootstrap_secret or os.environ.get("BOUNDARYLAB_BOOTSTRAP_SECRET")
    secret = configured_secret or secrets.token_urlsafe(18)
    if len(secret) < 16:
        parser.error("bootstrap secret must be at least 16 characters")
    if not configured_secret:
        print("Generated bootstrap secret (shown once):", secret)
    if args.target_config and args.with_lab_fixtures:
        parser.error("choose --target-config or --with-lab-fixtures, not both")
    targets = load_real_targets(args.target_config) if args.target_config else default_targets() if args.with_lab_fixtures else {}
    settings = Settings(
        database_path=args.data_dir / "boundarylab.db",
        bootstrap_secret=secret,
        targets=targets,
        openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
        ai_model=os.environ.get("BOUNDARYLAB_AI_MODEL", "gpt-6-astra"),
    )
    asyncio.run(serve(settings, args.host, with_lab_fixtures=args.with_lab_fixtures))


if __name__ == "__main__":
    main()
