from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

QuestionnaireCodeLiteral = Literal["PHQ-9", "GAD-7"]
AdherenceStatusLiteral = Literal["taken", "missed", "modified"]
SideEffectSeverityLiteral = Literal["mild", "moderate", "severe"]
SafetySourceLiteral = Literal["questionnaire", "side_effect"]
SafetyLevelLiteral = Literal["critical", "warning"]


class PatientQuestionnaireSummaryItem(BaseModel):
    assignment_id: UUID
    questionnaire_code: QuestionnaireCodeLiteral
    total_score: int
    has_safety_signal: bool
    submitted_at: datetime


class PatientAdherenceSummaryItem(BaseModel):
    id: UUID
    medication_id: UUID
    status: AdherenceStatusLiteral
    logged_at: datetime


class PatientSideEffectSummaryItem(BaseModel):
    id: UUID
    severity: SideEffectSeverityLiteral
    symptom: str
    reported_at: datetime


class PatientSafetyFlag(BaseModel):
    source: SafetySourceLiteral
    level: SafetyLevelLiteral
    code: str


class PatientSummaryResponse(BaseModel):
    patient_id: UUID
    questionnaires: list[PatientQuestionnaireSummaryItem]
    adherence: list[PatientAdherenceSummaryItem]
    side_effects: list[PatientSideEffectSummaryItem]
    safety_flags: list[PatientSafetyFlag]
