"""add exam_version_id and student_id to omr_attempt

Revision ID: 20260413_0004
Revises: 20260413_0003
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260413_0004"
down_revision = "20260413_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "omr_attempt",
        sa.Column("exam_version_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "omr_attempt",
        sa.Column("student_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_omr_attempt_exam_version_id", "omr_attempt", ["exam_version_id"], unique=False
    )
    op.create_index(
        "ix_omr_attempt_student_id", "omr_attempt", ["student_id"], unique=False
    )
    op.create_foreign_key(
        "fk_omr_attempt_exam_version",
        "omr_attempt",
        "exam_version",
        ["exam_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_omr_attempt_student",
        "omr_attempt",
        "student",
        ["student_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_omr_attempt_student", "omr_attempt", type_="foreignkey")
    op.drop_constraint("fk_omr_attempt_exam_version", "omr_attempt", type_="foreignkey")
    op.drop_index("ix_omr_attempt_student_id", table_name="omr_attempt")
    op.drop_index("ix_omr_attempt_exam_version_id", table_name="omr_attempt")
    op.drop_column("omr_attempt", "student_id")
    op.drop_column("omr_attempt", "exam_version_id")
