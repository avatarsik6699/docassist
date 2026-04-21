from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

QuestionnaireCodeLiteral = Literal["PHQ-9", "GAD-7"]
QuestionnaireStatusLiteral = Literal["assigned", "completed"]


class QuestionnaireAssignmentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    questionnaire_code: QuestionnaireCodeLiteral
    status: QuestionnaireStatusLiteral
    assigned_at: datetime
    completed_at: datetime | None
    total_score: int | None = None
    has_safety_signal: bool | None = None


class QuestionnaireAssignmentListResponse(BaseModel):
    items: list[QuestionnaireAssignmentItem]


class CreateQuestionnaireAssignmentRequest(BaseModel):
    questionnaire_code: QuestionnaireCodeLiteral


class QuestionnaireAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_user_id: UUID
    doctor_user_id: UUID
    questionnaire_code: QuestionnaireCodeLiteral
    status: QuestionnaireStatusLiteral
    assigned_at: datetime


class PendingQuestionnaireItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    questionnaire_code: QuestionnaireCodeLiteral
    status: Literal["assigned"]
    assigned_at: datetime


class PendingQuestionnaireListResponse(BaseModel):
    items: list[PendingQuestionnaireItem]


class SubmitQuestionnaireRequest(BaseModel):
    answers: dict[str, int] = Field(min_length=1)


class QuestionnaireSubmissionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    assignment_id: UUID
    questionnaire_code: QuestionnaireCodeLiteral
    total_score: int
    has_safety_signal: bool
    submitted_at: datetime
