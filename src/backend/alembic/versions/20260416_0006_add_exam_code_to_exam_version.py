"""add exam_code and teacher_id to exam_version

Revision ID: 20260416_0006
Revises: 20260413_0005
Create Date: 2026-04-16 15:05:00
"""

from __future__ import annotations

from collections import defaultdict

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "20260416_0006"
down_revision = "20260413_0005"
branch_labels = None
depends_on = None


def _next_numeric_code(used_codes: set[str]) -> str:
    candidate = 1
    while str(candidate) in used_codes:
        candidate += 1
    return str(candidate)


def upgrade() -> None:
    op.add_column("exam_version", sa.Column("teacher_id", sa.Integer(), nullable=True))
    op.add_column("exam_version", sa.Column("exam_code", sa.String(length=64), nullable=True))

    conn = op.get_bind()

    exam_rows = conn.execute(
        sa.text("SELECT id, teacher_id, exam_code FROM exam")
    ).mappings().all()
    exam_by_id = {int(row["id"]): row for row in exam_rows}

    versions = conn.execute(
        sa.text(
            "SELECT id, exam_id, created_at FROM exam_version "
            "ORDER BY exam_id ASC, created_at ASC, id ASC"
        )
    ).mappings().all()

    used_by_teacher: dict[int, set[str]] = defaultdict(set)
    for row in exam_rows:
        teacher_id = int(row["teacher_id"])
        used_by_teacher[teacher_id].add(str(row["exam_code"]))

    versions_by_exam: dict[int, list[dict]] = defaultdict(list)
    for row in versions:
        versions_by_exam[int(row["exam_id"])].append(row)

    updates: list[tuple[int, int, str]] = []
    for exam_id, version_rows in versions_by_exam.items():
        exam_row = exam_by_id.get(exam_id)
        if exam_row is None:
            continue
        teacher_id = int(exam_row["teacher_id"])
        used_codes = used_by_teacher[teacher_id]

        first_code = str(exam_row["exam_code"])
        first_version = version_rows[0]
        updates.append((int(first_version["id"]), teacher_id, first_code))
        used_codes.add(first_code)

        for version_row in version_rows[1:]:
            code = _next_numeric_code(used_codes)
            updates.append((int(version_row["id"]), teacher_id, code))
            used_codes.add(code)

    for version_id, teacher_id, exam_code in updates:
        conn.execute(
            sa.text(
                "UPDATE exam_version "
                "SET teacher_id = :teacher_id, exam_code = :exam_code "
                "WHERE id = :version_id"
            ),
            {"version_id": version_id, "teacher_id": teacher_id, "exam_code": exam_code},
        )

    op.alter_column("exam_version", "teacher_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("exam_version", "exam_code", existing_type=sa.String(length=64), nullable=False)

    op.create_index("ix_exam_version_teacher_id", "exam_version", ["teacher_id"], unique=False)
    op.create_index("ix_exam_version_exam_code", "exam_version", ["exam_code"], unique=False)
    op.create_unique_constraint(
        "uq_exam_version_teacher_code",
        "exam_version",
        ["teacher_id", "exam_code"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_exam_version_teacher_code", "exam_version", type_="unique")
    op.drop_index("ix_exam_version_exam_code", table_name="exam_version")
    op.drop_index("ix_exam_version_teacher_id", table_name="exam_version")
    op.drop_column("exam_version", "exam_code")
    op.drop_column("exam_version", "teacher_id")
