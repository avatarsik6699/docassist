from __future__ import annotations

import enum
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class OnboardingStatus(enum.StrEnum):
    pending = "pending"
    completed = "completed"


class PatientProfile(TimestampMixin, Base):
    __tablename__ = "patient_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    doctor_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    onboarding_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    must_change_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active_with_doctor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="patient_profile")
    doctor = relationship("User", foreign_keys=[doctor_user_id], back_populates="assigned_patients")
