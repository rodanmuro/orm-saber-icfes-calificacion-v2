"""add group key to exam_item

Revision ID: 20260527_0009
Revises: 20260430_0008
Create Date: 2026-05-27 09:20:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260527_0009"
down_revision = "20260430_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exam_item", sa.Column("group_key", sa.String(length=64), nullable=True))
    op.create_index("ix_exam_item_group_key", "exam_item", ["group_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_exam_item_group_key", table_name="exam_item")
    op.drop_column("exam_item", "group_key")
