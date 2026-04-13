from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Teacher(Base):
    __tablename__ = "teacher"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_uuid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(120))
    last_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list[Item]] = relationship(back_populates="teacher")
    exams: Mapped[list[Exam]] = relationship(back_populates="teacher")
    omr_attempts: Mapped[list[OmrAttempt]] = relationship(back_populates="teacher")


class Student(Base):
    __tablename__ = "student"
    __table_args__ = (UniqueConstraint("document_type", "document_number", name="uq_student_document"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_uuid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    document_type: Mapped[str] = mapped_column(String(16), index=True)
    document_number: Mapped[str] = mapped_column(String(32), index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(120))
    last_name: Mapped[str] = mapped_column(String(120))
    group_name: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Standard(Base):
    __tablename__ = "standard"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    competencies: Mapped[list[Competency]] = relationship(back_populates="standard")
    items: Mapped[list[Item]] = relationship(back_populates="standard")


class Competency(Base):
    __tablename__ = "competency"
    __table_args__ = (UniqueConstraint("standard_id", "name", name="uq_competency_standard_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(ForeignKey("standard.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    standard: Mapped[Standard] = relationship(back_populates="competencies")
    items: Mapped[list[Item]] = relationship(back_populates="competency")


class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher.id", ondelete="RESTRICT"), index=True)
    statement: Mapped[str] = mapped_column(Text)
    options: Mapped[dict[str, str]] = mapped_column(JSON)
    correct_answer: Mapped[str] = mapped_column(String(1))
    subject: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    difficulty: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    standard_id: Mapped[int | None] = mapped_column(
        ForeignKey("standard.id", ondelete="SET NULL"), nullable=True, index=True
    )
    competency_id: Mapped[int | None] = mapped_column(
        ForeignKey("competency.id", ondelete="SET NULL"), nullable=True, index=True
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    teacher: Mapped[Teacher] = relationship(back_populates="items")
    standard: Mapped[Standard | None] = relationship(back_populates="items")
    competency: Mapped[Competency | None] = relationship(back_populates="items")
    exam_items: Mapped[list[ExamItem]] = relationship(back_populates="item")


class Exam(Base):
    __tablename__ = "exam"
    __table_args__ = (UniqueConstraint("teacher_id", "exam_code", name="uq_exam_teacher_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher.id", ondelete="RESTRICT"), index=True)
    exam_code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    teacher: Mapped[Teacher] = relationship(back_populates="exams")
    exam_items: Mapped[list[ExamItem]] = relationship(
        back_populates="exam",
        order_by="ExamItem.order_position",
        cascade="all, delete-orphan",
    )
    exam_versions: Mapped[list[ExamVersion]] = relationship(
        back_populates="exam",
        order_by="ExamVersion.id",
        cascade="all, delete-orphan",
    )
    omr_attempts: Mapped[list[OmrAttempt]] = relationship(back_populates="exam")


class ExamItem(Base):
    __tablename__ = "exam_item"
    __table_args__ = (
        UniqueConstraint("exam_id", "item_id", name="uq_exam_item_pair"),
        UniqueConstraint("exam_id", "order_position", name="uq_exam_item_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exam.id", ondelete="CASCADE"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id", ondelete="RESTRICT"), index=True)
    order_position: Mapped[int] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exam: Mapped[Exam] = relationship(back_populates="exam_items")
    item: Mapped[Item] = relationship(back_populates="exam_items")


class ExamVersion(Base):
    __tablename__ = "exam_version"
    __table_args__ = (UniqueConstraint("exam_id", "version_code", name="uq_exam_version_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exam.id", ondelete="CASCADE"), index=True)
    version_code: Mapped[str] = mapped_column(String(64), index=True)
    seed_shuffle: Mapped[int] = mapped_column(Integer)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    shuffle_options: Mapped[bool] = mapped_column(Boolean, default=True)
    answer_key_json: Mapped[dict[str, str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exam: Mapped[Exam] = relationship(back_populates="exam_versions")
    version_items: Mapped[list[ExamVersionItem]] = relationship(
        back_populates="exam_version",
        order_by="ExamVersionItem.question_number",
        cascade="all, delete-orphan",
    )


class ExamVersionItem(Base):
    __tablename__ = "exam_version_item"
    __table_args__ = (
        UniqueConstraint("exam_version_id", "question_number", name="uq_exam_version_item_qnum"),
        UniqueConstraint("exam_version_id", "source_exam_item_id", name="uq_exam_version_item_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_version_id: Mapped[int] = mapped_column(
        ForeignKey("exam_version.id", ondelete="CASCADE"), index=True
    )
    source_exam_item_id: Mapped[int] = mapped_column(
        ForeignKey("exam_item.id", ondelete="RESTRICT"), index=True
    )
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id", ondelete="RESTRICT"), index=True)
    question_number: Mapped[int] = mapped_column(Integer, index=True)
    option_map_json: Mapped[dict[str, str]] = mapped_column(JSON)
    correct_answer_original: Mapped[str] = mapped_column(String(1))
    correct_answer_mapped: Mapped[str] = mapped_column(String(1))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exam_version: Mapped[ExamVersion] = relationship(back_populates="version_items")


class OmrAttempt(Base):
    __tablename__ = "omr_attempt"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teacher.id", ondelete="SET NULL"), nullable=True, index=True
    )
    exam_id: Mapped[int | None] = mapped_column(
        ForeignKey("exam.id", ondelete="SET NULL"), nullable=True, index=True
    )
    exam_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("exam_version.id", ondelete="SET NULL"), nullable=True, index=True
    )
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("student.id", ondelete="SET NULL"), nullable=True, index=True
    )
    exam_code_detected: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    score_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    blank_count: Mapped[int] = mapped_column(Integer, default=0)
    ambiguous_count: Mapped[int] = mapped_column(Integer, default=0)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_json_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    ratios_csv_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    auxiliary_ratios_csv_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher: Mapped[Teacher | None] = relationship(back_populates="omr_attempts")
    exam: Mapped[Exam | None] = relationship(back_populates="omr_attempts")
    exam_version: Mapped[ExamVersion | None] = relationship()
    student: Mapped[Student | None] = relationship()
    answers: Mapped[list[OmrAttemptAnswer]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="OmrAttemptAnswer.question_number",
    )


class OmrAttemptAnswer(Base):
    __tablename__ = "omr_attempt_answer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("omr_attempt.id", ondelete="CASCADE"), index=True)
    question_number: Mapped[int] = mapped_column(Integer, index=True)
    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    correct_answer: Mapped[str | None] = mapped_column(String(8), nullable=True)
    marked_answer: Mapped[str | None] = mapped_column(String(8), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    marked_options_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    attempt: Mapped[OmrAttempt] = relationship(back_populates="answers")
