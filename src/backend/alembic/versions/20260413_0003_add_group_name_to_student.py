"""add group_name to student

Revision ID: 20260413_0003
Revises: 20260315_0002
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260413_0003"
down_revision = "20260315_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "student",
        sa.Column("group_name", sa.String(length=64), nullable=False, server_default="SIN_GRUPO"),
    )
    op.alter_column("student", "group_name", server_default=None)


def downgrade() -> None:
    op.drop_column("student", "group_name")
