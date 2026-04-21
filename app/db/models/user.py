import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class UserRole(enum.StrEnum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    patient_profile = relationship(
        "PatientProfile",
        back_populates="user",
        uselist=False,
        foreign_keys="PatientProfile.user_id",
    )
    assigned_patients = relationship(
        "PatientProfile",
        back_populates="doctor",
        foreign_keys="PatientProfile.doctor_user_id",
    )
    medications = relationship("Medication", foreign_keys="Medication.patient_user_id")
    managed_medications = relationship("Medication", foreign_keys="Medication.doctor_user_id")
    adherence_logs = relationship("AdherenceLog", foreign_keys="AdherenceLog.patient_user_id")
    questionnaire_assignments = relationship(
        "QuestionnaireAssignment",
        foreign_keys="QuestionnaireAssignment.patient_user_id",
    )
    managed_questionnaire_assignments = relationship(
        "QuestionnaireAssignment",
        foreign_keys="QuestionnaireAssignment.doctor_user_id",
    )
    questionnaire_responses = relationship(
        "QuestionnaireResponse",
        foreign_keys="QuestionnaireResponse.patient_user_id",
    )
