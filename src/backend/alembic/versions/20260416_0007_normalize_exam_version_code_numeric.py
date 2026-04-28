"""normalize exam_version.version_code to numeric sequence per exam

Revision ID: 20260416_0007
Revises: 20260416_0006
Create Date: 2026-04-16 16:05:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260416_0007"
down_revision = "20260416_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            WITH ranked AS (
              SELECT
                id,
                exam_id,
                ROW_NUMBER() OVER (PARTITION BY exam_id ORDER BY created_at ASC, id ASC) AS rn
              FROM exam_version
            )
            UPDATE exam_version ev
            SET version_code = ranked.rn::text
            FROM ranked
            WHERE ev.id = ranked.id
            """
        )
    )


def downgrade() -> None:
    # Irreversible normalization: keep as-is on downgrade.
    pass
