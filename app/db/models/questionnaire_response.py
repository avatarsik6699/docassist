from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class QuestionnaireResponse(UUIDMixin, Base):
    __tablename__ = "questionnaire_responses"

    assignment_id: Mapped[UUID] = mapped_column(
        ForeignKey("questionnaire_assignments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    patient_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    questionnaire_code: Mapped[str] = mapped_column(String(16), nullable=False)
    answers: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    has_safety_signal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    assignment = relationship("QuestionnaireAssignment", back_populates="response")
    patient = relationship(
        "User",
        foreign_keys=[patient_user_id],
        back_populates="questionnaire_responses",
    )
