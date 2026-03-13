from __future__ import annotations

import json
import os
from dataclasses import dataclass

from sqlalchemy import create_engine, select
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
    standard_code: str
    competency_code: str


def _norm(value: str | None) -> str:
    return (value or "").strip()


def _item_signature(item: Item, standard_code: str, competency_code: str) -> ItemSignature:
    options_payload = item.options or {}
    return ItemSignature(
        teacher_id=item.teacher_id,
        statement=_norm(item.statement),
        options_json=json.dumps(options_payload, ensure_ascii=False, sort_keys=True),
        correct_answer=_norm(item.correct_answer),
        subject=_norm(item.subject),
        difficulty=_norm(item.difficulty),
        standard_code=_norm(standard_code),
        competency_code=_norm(competency_code),
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

    SqliteSession = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False, future=True)
    PostgresSession = sessionmaker(bind=postgres_engine, autoflush=False, autocommit=False, future=True)

    created_teachers = 0
    created_standards = 0
    created_competencies = 0
    created_items = 0
    skipped_items = 0

    with SqliteSession() as sqlite_db, PostgresSession() as pg_db:
        sqlite_teachers = sqlite_db.scalars(select(Teacher).order_by(Teacher.id.asc())).all()
        teacher_id_map: dict[int, int] = {}
        for t in sqlite_teachers:
            existing = pg_db.scalar(select(Teacher).where(Teacher.email == t.email))
            if existing is None:
                existing = Teacher(
                    external_uuid=t.external_uuid,
                    email=t.email,
                    first_name=t.first_name,
                    last_name=t.last_name,
                )
                pg_db.add(existing)
                pg_db.flush()
                created_teachers += 1
            teacher_id_map[t.id] = existing.id

        sqlite_standards = sqlite_db.scalars(select(Standard).order_by(Standard.id.asc())).all()
        standard_code_to_pg_id: dict[str, int] = {}
        standard_id_to_code: dict[int, str] = {}
        for s in sqlite_standards:
            standard_id_to_code[s.id] = s.code
            existing = pg_db.scalar(select(Standard).where(Standard.code == s.code))
            if existing is None:
                existing = Standard(code=s.code, name=s.name)
                pg_db.add(existing)
                pg_db.flush()
                created_standards += 1
            elif not _norm(existing.name):
                existing.name = s.name
            standard_code_to_pg_id[s.code] = existing.id

        sqlite_competencies = sqlite_db.scalars(select(Competency).order_by(Competency.id.asc())).all()
        competency_key_to_pg_id: dict[tuple[str, str], int] = {}
        competency_id_to_key: dict[int, tuple[str, str]] = {}
        for c in sqlite_competencies:
            standard_code = standard_id_to_code.get(c.standard_id)
            if not standard_code:
                continue
            competency_id_to_key[c.id] = (standard_code, c.code)
            target_standard_id = standard_code_to_pg_id[standard_code]
            existing = pg_db.scalar(
                select(Competency).where(
                    Competency.standard_id == target_standard_id,
                    Competency.code == c.code,
                )
            )
            if existing is None:
                existing = Competency(
                    standard_id=target_standard_id,
                    code=c.code,
                    name=c.name,
                )
                pg_db.add(existing)
                pg_db.flush()
                created_competencies += 1
            elif not _norm(existing.name):
                existing.name = c.name
            competency_key_to_pg_id[(standard_code, c.code)] = existing.id

        existing_signatures: set[ItemSignature] = set()
        for pg_item in pg_db.scalars(select(Item)).all():
            std_code = pg_item.standard.code if pg_item.standard else ""
            comp_code = pg_item.competency.code if pg_item.competency else ""
            existing_signatures.add(_item_signature(pg_item, std_code, comp_code))

        sqlite_items = sqlite_db.scalars(select(Item).order_by(Item.id.asc())).all()
        for row in sqlite_items:
            mapped_teacher_id = teacher_id_map.get(row.teacher_id)
            if mapped_teacher_id is None:
                continue

            standard_code = ""
            if row.standard_id:
                standard_code = standard_id_to_code.get(row.standard_id, "")
            mapped_standard_id = standard_code_to_pg_id.get(standard_code) if standard_code else None

            competency_code = ""
            mapped_competency_id = None
            if row.competency_id:
                key = competency_id_to_key.get(row.competency_id)
                if key:
                    standard_code_from_comp, competency_code = key
                    if not standard_code:
                        standard_code = standard_code_from_comp
                        mapped_standard_id = standard_code_to_pg_id.get(standard_code)
                    mapped_competency_id = competency_key_to_pg_id.get(key)

            candidate = Item(
                teacher_id=mapped_teacher_id,
                statement=row.statement,
                options=row.options,
                correct_answer=row.correct_answer,
                subject=row.subject,
                difficulty=row.difficulty,
                standard_id=mapped_standard_id,
                competency_id=mapped_competency_id,
                metadata_json=row.metadata_json,
            )
            sig = _item_signature(candidate, standard_code, competency_code)

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

