from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

AdherenceStatusLiteral = Literal["taken", "missed", "modified"]


class MedicationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    dosage_instructions: str
    is_active: bool


class MedicationListResponse(BaseModel):
    items: list[MedicationItem]


class CreateMedicationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    dosage_instructions: str = Field(min_length=1, max_length=1000)
    is_active: bool = True


class MedicationOut(MedicationItem):
    patient_user_id: UUID
    doctor_user_id: UUID


class CreateAdherenceLogRequest(BaseModel):
    status: AdherenceStatusLiteral
    deviation_note: str | None = Field(default=None, max_length=2000)
    logged_at: datetime | None = None


class AdherenceLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    medication_id: UUID
    status: AdherenceStatusLiteral
    deviation_note: str | None
    logged_at: datetime


class AdherenceLogListResponse(BaseModel):
    items: list[AdherenceLogItem]
