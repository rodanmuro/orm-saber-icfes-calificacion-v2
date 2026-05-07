"""add anonymous_exam and omr_attempt.anonymous_exam_id

Revision ID: 20260430_0008
Revises: 20260416_0007
Create Date: 2026-04-30 10:40:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260430_0008"
down_revision = "20260416_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "anonymous_exam",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("exam_code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("answer_key_json", sa.JSON(), nullable=False),
        sa.Column("source_pdf_path", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("teacher_id", "exam_code", name="uq_anonymous_exam_teacher_code"),
    )
    op.create_index(op.f("ix_anonymous_exam_teacher_id"), "anonymous_exam", ["teacher_id"], unique=False)
    op.create_index(op.f("ix_anonymous_exam_exam_code"), "anonymous_exam", ["exam_code"], unique=False)

    op.add_column("omr_attempt", sa.Column("anonymous_exam_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_omr_attempt_anonymous_exam_id"), "omr_attempt", ["anonymous_exam_id"], unique=False)
    op.create_foreign_key(
        "fk_omr_attempt_anonymous_exam_id",
        "omr_attempt",
        "anonymous_exam",
        ["anonymous_exam_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_omr_attempt_anonymous_exam_id", "omr_attempt", type_="foreignkey")
    op.drop_index(op.f("ix_omr_attempt_anonymous_exam_id"), table_name="omr_attempt")
    op.drop_column("omr_attempt", "anonymous_exam_id")

    op.drop_index(op.f("ix_anonymous_exam_exam_code"), table_name="anonymous_exam")
    op.drop_index(op.f("ix_anonymous_exam_teacher_id"), table_name="anonymous_exam")
    op.drop_table("anonymous_exam")
