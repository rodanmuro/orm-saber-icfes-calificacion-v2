"""add manual override to omr_attempt_answer

Revision ID: 20260413_0005
Revises: 20260413_0004
Create Date: 2026-04-13 16:02:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260413_0005"
down_revision = "20260413_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("omr_attempt_answer", sa.Column("manual_answer", sa.String(length=8), nullable=True))
    op.add_column(
        "omr_attempt_answer",
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.alter_column("omr_attempt_answer", "manual_override", server_default=None)


def downgrade() -> None:
    op.drop_column("omr_attempt_answer", "manual_override")
    op.drop_column("omr_attempt_answer", "manual_answer")
