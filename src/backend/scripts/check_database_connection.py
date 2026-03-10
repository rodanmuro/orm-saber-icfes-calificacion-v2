from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine


def main() -> int:
    url = settings.database_url
    print(f"[db-check] DATABASE_URL={url}")

    try:
        with engine.connect() as conn:
            value = conn.execute(text("SELECT 1")).scalar_one()
            print(f"[db-check] OK - SELECT 1 => {value}")
            return 0
    except SQLAlchemyError as exc:
        print(f"[db-check] ERROR - No fue posible conectar: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
