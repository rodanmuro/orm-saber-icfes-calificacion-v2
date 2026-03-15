"""drop code columns from standard and competency, use name as unique identifier

Revision ID: 20260315_0002
Revises: 20260310_0001
Create Date: 2026-03-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260315_0002"
down_revision: Union[str, None] = "20260310_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- standard ---
    op.drop_index("ix_standard_code", table_name="standard", if_exists=True)
    op.drop_column("standard", "code")
    op.create_index("ix_standard_name", "standard", ["name"], unique=True)

    # --- competency ---
    op.drop_constraint("uq_competency_standard_code", "competency", type_="unique")
    op.drop_index("ix_competency_code", table_name="competency", if_exists=True)
    op.drop_column("competency", "code")
    op.create_unique_constraint("uq_competency_standard_name", "competency", ["standard_id", "name"])


def downgrade() -> None:
    # --- competency ---
    op.drop_constraint("uq_competency_standard_name", "competency", type_="unique")
    op.add_column("competency", sa.Column("code", sa.String(length=64), nullable=False, server_default="restored"))
    op.create_index("ix_competency_code", "competency", ["code"], unique=False)
    op.create_unique_constraint("uq_competency_standard_code", "competency", ["standard_id", "code"])

    # --- standard ---
    op.drop_index("ix_standard_name", table_name="standard")
    op.add_column("standard", sa.Column("code", sa.String(length=64), nullable=False, server_default="restored"))
    op.create_index("ix_standard_code", "standard", ["code"], unique=True)
