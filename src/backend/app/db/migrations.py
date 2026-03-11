from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

from app.core.config import settings


LEGACY_SCHEMA_TABLES = {
    "teacher",
    "item",
    "exam",
    "exam_item",
    "exam_version",
    "exam_version_item",
}


def _run_alembic(backend_root: Path, *args: str) -> None:
    alembic_ini = backend_root / "alembic.ini"
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(alembic_ini), *args],
        check=True,
        cwd=str(backend_root),
    )


def _needs_legacy_stamp(database_url: str) -> bool:
    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        alembic_has_rows = False
        if "alembic_version" in table_names:
            with engine.connect() as connection:
                rows = connection.execute(
                    text("SELECT COUNT(*) FROM alembic_version")
                ).scalar_one()
                alembic_has_rows = rows > 0
    finally:
        engine.dispose()

    has_alembic_version = "alembic_version" in table_names
    has_legacy_schema = bool(table_names.intersection(LEGACY_SCHEMA_TABLES))
    if (not has_alembic_version) and has_legacy_schema:
        return True
    if has_alembic_version and (not alembic_has_rows) and has_legacy_schema:
        return True
    return False


def run_migrations() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    if _needs_legacy_stamp(settings.database_url):
        _run_alembic(backend_root, "stamp", "head")
    _run_alembic(backend_root, "upgrade", "head")
