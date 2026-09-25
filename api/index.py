import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "service" / "src"))

from boundarylab.app import Settings, create_app, default_targets

# Serverless fallback for Vercel / ephemeral environments
secret = os.environ.get("BOUNDARYLAB_BOOTSTRAP_SECRET", "boundarylab-bootstrap-secret-16chars")
data_dir = Path("/tmp") if os.environ.get("VERCEL") else ROOT / "var"

settings = Settings(
    database_path=data_dir / "boundarylab.db",
    bootstrap_secret=secret,
    targets=default_targets(),
    secure_cookie=os.environ.get("BOUNDARYLAB_SECURE_COOKIE", "false").lower() == "true",
    openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
)

app = create_app(settings)
