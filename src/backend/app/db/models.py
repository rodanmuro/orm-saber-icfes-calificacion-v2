from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, func
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Standard(Base):
    __tablename__ = "standard"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    competencies: Mapped[list[Competency]] = relationship(back_populates="standard")
    items: Mapped[list[Item]] = relationship(back_populates="standard")


class Competency(Base):
    __tablename__ = "competency"
    __table_args__ = (UniqueConstraint("standard_id", "code", name="uq_competency_standard_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(ForeignKey("standard.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
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

