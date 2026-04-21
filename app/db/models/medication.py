from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Medication(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "medications"

    patient_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    patient = relationship("User", foreign_keys=[patient_user_id], back_populates="medications")
    doctor = relationship(
        "User", foreign_keys=[doctor_user_id], back_populates="managed_medications"
    )
    adherence_logs = relationship(
        "AdherenceLog",
        back_populates="medication",
        cascade="all, delete-orphan",
        order_by="desc(AdherenceLog.logged_at)",
    )
