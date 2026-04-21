from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class SideEffectReport(UUIDMixin, Base):
    __tablename__ = "side_effect_reports"

    patient_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    medication_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("medications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    symptom: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    patient = relationship(
        "User",
        foreign_keys=[patient_user_id],
        back_populates="side_effect_reports",
    )
    doctor = relationship(
        "User",
        foreign_keys=[doctor_user_id],
        back_populates="managed_side_effect_reports",
    )
    medication = relationship("Medication", back_populates="side_effect_reports")
