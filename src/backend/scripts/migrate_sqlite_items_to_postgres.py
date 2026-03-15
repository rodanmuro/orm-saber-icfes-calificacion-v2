from __future__ import annotations

import json
import os
from dataclasses import dataclass

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Competency, Item, Standard, Teacher


@dataclass(frozen=True)
class ItemSignature:
    teacher_id: int
    statement: str
    options_json: str
    correct_answer: str
    subject: str
    difficulty: str
    standard_name: str
    competency_name: str


def _norm(value: str | None) -> str:
    return (value or "").strip()


def _item_signature(item: Item, standard_name: str, competency_name: str) -> ItemSignature:
    options_payload = item.options or {}
    return ItemSignature(
        teacher_id=item.teacher_id,
        statement=_norm(item.statement),
        options_json=json.dumps(options_payload, ensure_ascii=False, sort_keys=True),
        correct_answer=_norm(item.correct_answer),
        subject=_norm(item.subject),
        difficulty=_norm(item.difficulty),
        standard_name=_norm(standard_name),
        competency_name=_norm(competency_name),
    )


def _require_postgres_url() -> str:
    url = os.getenv("POSTGRES_DATABASE_URL") or os.getenv("DATABASE_URL") or ""
    if not url.startswith("postgresql+psycopg://"):
        raise RuntimeError(
            "Define POSTGRES_DATABASE_URL (o DATABASE_URL) con un valor postgresql+psycopg://..."
        )
    return url


def _sqlite_url() -> str:
    return os.getenv("SQLITE_DATABASE_URL", "sqlite:///data/omr_app.db")


def main() -> None:
    sqlite_url = _sqlite_url()
    postgres_url = _require_postgres_url()

    sqlite_engine = create_engine(sqlite_url, future=True)
    postgres_engine = create_engine(postgres_url, future=True)

    PostgresSession = sessionmaker(bind=postgres_engine, autoflush=False, autocommit=False, future=True)

    created_teachers = 0
    created_standards = 0
    created_competencies = 0
    created_items = 0
    skipped_items = 0

    # Leer todo desde SQLite con SQL crudo (el modelo ORM ya no tiene 'code')
    with sqlite_engine.connect() as sqlite_conn:
        sqlite_teachers = sqlite_conn.execute(text(
            "SELECT id, external_uuid, email, first_name, last_name FROM teacher ORDER BY id"
        )).mappings().all()

        sqlite_standards = sqlite_conn.execute(text(
            "SELECT id, name FROM standard ORDER BY id"
        )).mappings().all()

        sqlite_competencies = sqlite_conn.execute(text(
            "SELECT id, standard_id, name FROM competency ORDER BY id"
        )).mappings().all()

        sqlite_items = sqlite_conn.execute(text(
            "SELECT id, teacher_id, statement, options, correct_answer, subject, difficulty, "
            "standard_id, competency_id, metadata_json FROM item ORDER BY id"
        )).mappings().all()

    with PostgresSession() as pg_db:
        # --- Teachers ---
        teacher_id_map: dict[int, int] = {}
        for t in sqlite_teachers:
            existing = pg_db.scalar(select(Teacher).where(Teacher.email == t["email"]))
            if existing is None:
                existing = Teacher(
                    external_uuid=t["external_uuid"],
                    email=t["email"],
                    first_name=t["first_name"],
                    last_name=t["last_name"],
                )
                pg_db.add(existing)
                pg_db.flush()
                created_teachers += 1
            teacher_id_map[t["id"]] = existing.id

        # --- Standards (match por name) ---
        standard_sqlite_id_to_pg_id: dict[int, int] = {}
        standard_sqlite_id_to_name: dict[int, str] = {}
        for s in sqlite_standards:
            standard_sqlite_id_to_name[s["id"]] = _norm(s["name"])
            existing = pg_db.scalar(select(Standard).where(Standard.name == _norm(s["name"])))
            if existing is None:
                existing = Standard(name=_norm(s["name"]))
                pg_db.add(existing)
                pg_db.flush()
                created_standards += 1
            standard_sqlite_id_to_pg_id[s["id"]] = existing.id

        # --- Competencies (match por standard_id + name) ---
        competency_sqlite_id_to_pg_id: dict[int, int] = {}
        competency_sqlite_id_to_name: dict[int, str] = {}
        for c in sqlite_competencies:
            pg_standard_id = standard_sqlite_id_to_pg_id.get(c["standard_id"])
            if pg_standard_id is None:
                continue
            comp_name = _norm(c["name"])
            competency_sqlite_id_to_name[c["id"]] = comp_name
            existing = pg_db.scalar(
                select(Competency).where(
                    Competency.standard_id == pg_standard_id,
                    Competency.name == comp_name,
                )
            )
            if existing is None:
                existing = Competency(standard_id=pg_standard_id, name=comp_name)
                pg_db.add(existing)
                pg_db.flush()
                created_competencies += 1
            competency_sqlite_id_to_pg_id[c["id"]] = existing.id

        # --- Firmas de items ya en Postgres ---
        existing_signatures: set[ItemSignature] = set()
        for pg_item in pg_db.scalars(select(Item)).all():
            std_name = pg_item.standard.name if pg_item.standard else ""
            comp_name = pg_item.competency.name if pg_item.competency else ""
            existing_signatures.add(_item_signature(pg_item, std_name, comp_name))

        # --- Items ---
        for row in sqlite_items:
            mapped_teacher_id = teacher_id_map.get(row["teacher_id"])
            if mapped_teacher_id is None:
                continue

            mapped_standard_id = standard_sqlite_id_to_pg_id.get(row["standard_id"]) if row["standard_id"] else None
            mapped_competency_id = competency_sqlite_id_to_pg_id.get(row["competency_id"]) if row["competency_id"] else None

            std_name = standard_sqlite_id_to_name.get(row["standard_id"], "") if row["standard_id"] else ""
            comp_name = competency_sqlite_id_to_name.get(row["competency_id"], "") if row["competency_id"] else ""

            options = row["options"] if isinstance(row["options"], dict) else json.loads(row["options"] or "{}")
            metadata = row["metadata_json"] if isinstance(row["metadata_json"], dict) else (
                json.loads(row["metadata_json"]) if row["metadata_json"] else None
            )

            candidate = Item(
                teacher_id=mapped_teacher_id,
                statement=row["statement"],
                options=options,
                correct_answer=row["correct_answer"],
                subject=row["subject"],
                difficulty=row["difficulty"],
                standard_id=mapped_standard_id,
                competency_id=mapped_competency_id,
                metadata_json=metadata,
            )
            sig = _item_signature(candidate, std_name, comp_name)

            if sig in existing_signatures:
                skipped_items += 1
                continue

            pg_db.add(candidate)
            existing_signatures.add(sig)
            created_items += 1

        pg_db.commit()

    sqlite_engine.dispose()
    postgres_engine.dispose()

    print("[sqlite->postgres] migration completed")
    print(f"[sqlite->postgres] created_teachers={created_teachers}")
    print(f"[sqlite->postgres] created_standards={created_standards}")
    print(f"[sqlite->postgres] created_competencies={created_competencies}")
    print(f"[sqlite->postgres] created_items={created_items}")
    print(f"[sqlite->postgres] skipped_items={skipped_items}")


if __name__ == "__main__":
    main()
