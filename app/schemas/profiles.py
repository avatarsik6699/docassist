from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

OnboardingStatusLiteral = Literal["pending", "completed"]


class PatientRosterItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    is_active: bool
    onboarding_status: OnboardingStatusLiteral


class PatientRosterResponse(BaseModel):
    items: list[PatientRosterItem]


class CreatePatientRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class CreatePatientResponse(BaseModel):
    id: UUID
    email: str
    doctor_user_id: UUID
    onboarding_status: Literal["pending"]
    temporary_password: str


class ActivatePatientResponse(BaseModel):
    id: UUID
    is_active: bool
    onboarding_status: OnboardingStatusLiteral


class SetupAccountRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=255)
