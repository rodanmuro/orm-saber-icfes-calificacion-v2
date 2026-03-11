"""initial schema

Revision ID: 20260310_0001
Revises:
Create Date: 2026-03-10 09:55:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260310_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teacher",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_uuid", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teacher_external_uuid", "teacher", ["external_uuid"], unique=True)
    op.create_index("ix_teacher_email", "teacher", ["email"], unique=True)

    op.create_table(
        "student",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_uuid", sa.String(length=64), nullable=False),
        sa.Column("document_type", sa.String(length=16), nullable=False),
        sa.Column("document_number", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_type", "document_number", name="uq_student_document"),
    )
    op.create_index("ix_student_external_uuid", "student", ["external_uuid"], unique=True)
    op.create_index("ix_student_document_type", "student", ["document_type"], unique=False)
    op.create_index("ix_student_document_number", "student", ["document_number"], unique=False)
    op.create_index("ix_student_email", "student", ["email"], unique=True)

    op.create_table(
        "standard",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_standard_code", "standard", ["code"], unique=True)

    op.create_table(
        "competency",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("standard_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["standard_id"], ["standard.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("standard_id", "code", name="uq_competency_standard_code"),
    )
    op.create_index("ix_competency_standard_id", "competency", ["standard_id"], unique=False)
    op.create_index("ix_competency_code", "competency", ["code"], unique=False)

    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("subject", sa.String(length=120), nullable=True),
        sa.Column("difficulty", sa.String(length=32), nullable=True),
        sa.Column("standard_id", sa.Integer(), nullable=True),
        sa.Column("competency_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["competency_id"], ["competency.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["standard_id"], ["standard.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_item_teacher_id", "item", ["teacher_id"], unique=False)
    op.create_index("ix_item_subject", "item", ["subject"], unique=False)
    op.create_index("ix_item_difficulty", "item", ["difficulty"], unique=False)
    op.create_index("ix_item_standard_id", "item", ["standard_id"], unique=False)
    op.create_index("ix_item_competency_id", "item", ["competency_id"], unique=False)

    op.create_table(
        "exam",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("exam_code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("teacher_id", "exam_code", name="uq_exam_teacher_code"),
    )
    op.create_index("ix_exam_teacher_id", "exam", ["teacher_id"], unique=False)
    op.create_index("ix_exam_exam_code", "exam", ["exam_code"], unique=False)

    op.create_table(
        "exam_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("order_position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exam.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exam_id", "item_id", name="uq_exam_item_pair"),
        sa.UniqueConstraint("exam_id", "order_position", name="uq_exam_item_order"),
    )
    op.create_index("ix_exam_item_exam_id", "exam_item", ["exam_id"], unique=False)
    op.create_index("ix_exam_item_item_id", "exam_item", ["item_id"], unique=False)
    op.create_index("ix_exam_item_order_position", "exam_item", ["order_position"], unique=False)

    op.create_table(
        "exam_version",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("version_code", sa.String(length=64), nullable=False),
        sa.Column("seed_shuffle", sa.Integer(), nullable=False),
        sa.Column("shuffle_questions", sa.Boolean(), nullable=False),
        sa.Column("shuffle_options", sa.Boolean(), nullable=False),
        sa.Column("answer_key_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exam.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exam_id", "version_code", name="uq_exam_version_code"),
    )
    op.create_index("ix_exam_version_exam_id", "exam_version", ["exam_id"], unique=False)
    op.create_index("ix_exam_version_version_code", "exam_version", ["version_code"], unique=False)

    op.create_table(
        "exam_version_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exam_version_id", sa.Integer(), nullable=False),
        sa.Column("source_exam_item_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("option_map_json", sa.JSON(), nullable=False),
        sa.Column("correct_answer_original", sa.String(length=1), nullable=False),
        sa.Column("correct_answer_mapped", sa.String(length=1), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exam_version_id"], ["exam_version.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_exam_item_id"], ["exam_item.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exam_version_id", "question_number", name="uq_exam_version_item_qnum"),
        sa.UniqueConstraint("exam_version_id", "source_exam_item_id", name="uq_exam_version_item_source"),
    )
    op.create_index("ix_exam_version_item_version_id", "exam_version_item", ["exam_version_id"], unique=False)
    op.create_index("ix_exam_version_item_item_id", "exam_version_item", ["item_id"], unique=False)
    op.create_index("ix_exam_version_item_qnum", "exam_version_item", ["question_number"], unique=False)

    op.create_table(
        "omr_attempt",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=True),
        sa.Column("exam_id", sa.Integer(), nullable=True),
        sa.Column("exam_code_detected", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("score_percent", sa.Float(), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("incorrect_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("blank_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("ambiguous_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("manual_review_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("uploaded_image_path", sa.Text(), nullable=True),
        sa.Column("trace_json_path", sa.Text(), nullable=True),
        sa.Column("ratios_csv_path", sa.Text(), nullable=True),
        sa.Column("auxiliary_ratios_csv_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exam.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_omr_attempt_teacher_id", "omr_attempt", ["teacher_id"], unique=False)
    op.create_index("ix_omr_attempt_exam_id", "omr_attempt", ["exam_id"], unique=False)
    op.create_index("ix_omr_attempt_exam_code_detected", "omr_attempt", ["exam_code_detected"], unique=False)
    op.create_index("ix_omr_attempt_status", "omr_attempt", ["status"], unique=False)

    op.create_table(
        "omr_attempt_answer",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("correct_answer", sa.String(length=8), nullable=True),
        sa.Column("marked_answer", sa.String(length=8), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("marked_options_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["attempt_id"], ["omr_attempt.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_omr_attempt_answer_attempt_id", "omr_attempt_answer", ["attempt_id"], unique=False)
    op.create_index("ix_omr_attempt_answer_question_number", "omr_attempt_answer", ["question_number"], unique=False)
    op.create_index("ix_omr_attempt_answer_item_id", "omr_attempt_answer", ["item_id"], unique=False)
    op.create_index("ix_omr_attempt_answer_status", "omr_attempt_answer", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_omr_attempt_answer_status", table_name="omr_attempt_answer")
    op.drop_index("ix_omr_attempt_answer_item_id", table_name="omr_attempt_answer")
    op.drop_index("ix_omr_attempt_answer_question_number", table_name="omr_attempt_answer")
    op.drop_index("ix_omr_attempt_answer_attempt_id", table_name="omr_attempt_answer")
    op.drop_table("omr_attempt_answer")

    op.drop_index("ix_omr_attempt_status", table_name="omr_attempt")
    op.drop_index("ix_omr_attempt_exam_code_detected", table_name="omr_attempt")
    op.drop_index("ix_omr_attempt_exam_id", table_name="omr_attempt")
    op.drop_index("ix_omr_attempt_teacher_id", table_name="omr_attempt")
    op.drop_table("omr_attempt")

    op.drop_index("ix_exam_version_item_qnum", table_name="exam_version_item")
    op.drop_index("ix_exam_version_item_item_id", table_name="exam_version_item")
    op.drop_index("ix_exam_version_item_version_id", table_name="exam_version_item")
    op.drop_table("exam_version_item")

    op.drop_index("ix_exam_version_version_code", table_name="exam_version")
    op.drop_index("ix_exam_version_exam_id", table_name="exam_version")
    op.drop_table("exam_version")

    op.drop_index("ix_exam_item_order_position", table_name="exam_item")
    op.drop_index("ix_exam_item_item_id", table_name="exam_item")
    op.drop_index("ix_exam_item_exam_id", table_name="exam_item")
    op.drop_table("exam_item")

    op.drop_index("ix_exam_exam_code", table_name="exam")
    op.drop_index("ix_exam_teacher_id", table_name="exam")
    op.drop_table("exam")

    op.drop_index("ix_item_competency_id", table_name="item")
    op.drop_index("ix_item_standard_id", table_name="item")
    op.drop_index("ix_item_difficulty", table_name="item")
    op.drop_index("ix_item_subject", table_name="item")
    op.drop_index("ix_item_teacher_id", table_name="item")
    op.drop_table("item")

    op.drop_index("ix_competency_code", table_name="competency")
    op.drop_index("ix_competency_standard_id", table_name="competency")
    op.drop_table("competency")

    op.drop_index("ix_standard_code", table_name="standard")
    op.drop_table("standard")

    op.drop_index("ix_student_email", table_name="student")
    op.drop_index("ix_student_document_number", table_name="student")
    op.drop_index("ix_student_document_type", table_name="student")
    op.drop_index("ix_student_external_uuid", table_name="student")
    op.drop_table("student")

    op.drop_index("ix_teacher_email", table_name="teacher")
    op.drop_index("ix_teacher_external_uuid", table_name="teacher")
    op.drop_table("teacher")
