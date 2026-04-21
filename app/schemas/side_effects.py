from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

SideEffectSeverityLiteral = Literal["mild", "moderate", "severe"]


class CreateSideEffectReportRequest(BaseModel):
    severity: SideEffectSeverityLiteral
    symptom: str = Field(min_length=1, max_length=2000)
    note: str | None = Field(default=None, max_length=2000)
    medication_id: UUID | None = None
    reported_at: datetime | None = None


class SideEffectReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_user_id: UUID
    doctor_user_id: UUID
    medication_id: UUID | None
    severity: SideEffectSeverityLiteral
    symptom: str
    note: str | None
    reported_at: datetime


class SideEffectReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    severity: SideEffectSeverityLiteral
    symptom: str
    note: str | None
    reported_at: datetime


class SideEffectReportListResponse(BaseModel):
    items: list[SideEffectReportItem]
