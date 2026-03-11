from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def run_migrations() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    alembic_ini = backend_root / "alembic.ini"
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(alembic_ini), "upgrade", "head"],
        check=True,
        cwd=str(backend_root),
    )
