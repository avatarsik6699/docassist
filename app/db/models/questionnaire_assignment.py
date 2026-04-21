from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class QuestionnaireCode(enum.StrEnum):
    phq9 = "PHQ-9"
    gad7 = "GAD-7"


class QuestionnaireAssignmentStatus(enum.StrEnum):
    assigned = "assigned"
    completed = "completed"


class QuestionnaireAssignment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "questionnaire_assignments"

    patient_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    questionnaire_code: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=QuestionnaireAssignmentStatus.assigned.value,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    patient = relationship(
        "User",
        foreign_keys=[patient_user_id],
        back_populates="questionnaire_assignments",
    )
    doctor = relationship(
        "User",
        foreign_keys=[doctor_user_id],
        back_populates="managed_questionnaire_assignments",
    )
    response = relationship(
        "QuestionnaireResponse",
        back_populates="assignment",
        uselist=False,
        cascade="all, delete-orphan",
    )
