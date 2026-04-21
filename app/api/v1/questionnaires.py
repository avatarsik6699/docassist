from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import Role, require_role
from app.db.models.patient_profile import PatientProfile
from app.db.models.questionnaire_assignment import (
    QuestionnaireAssignment,
    QuestionnaireAssignmentStatus,
    QuestionnaireCode,
)
from app.db.models.questionnaire_response import QuestionnaireResponse
from app.db.models.user import User, UserRole
from app.db.session import get_db
from app.schemas.questionnaires import (
    CreateQuestionnaireAssignmentRequest,
    PendingQuestionnaireItem,
    PendingQuestionnaireListResponse,
    QuestionnaireAssignmentItem,
    QuestionnaireAssignmentListResponse,
    QuestionnaireAssignmentOut,
    QuestionnaireSubmissionResult,
    SubmitQuestionnaireRequest,
)

router = APIRouter(tags=["questionnaires"])

PHQ9_QUESTION_IDS = [f"q{i}" for i in range(1, 10)]
GAD7_QUESTION_IDS = [f"q{i}" for i in range(1, 8)]
QUESTIONNAIRE_QUESTION_IDS = {
    QuestionnaireCode.phq9.value: PHQ9_QUESTION_IDS,
    QuestionnaireCode.gad7.value: GAD7_QUESTION_IDS,
}


async def _get_assigned_patient_or_404(
    db: AsyncSession, doctor_id: UUID, patient_id: UUID
) -> PatientProfile:
    result = await db.execute(
        select(PatientProfile)
        .join(User, User.id == PatientProfile.user_id)
        .where(
            PatientProfile.user_id == patient_id,
            PatientProfile.doctor_user_id == doctor_id,
            User.role == UserRole.patient,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return profile


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _score_answers(
    questionnaire_code: str, answers: dict[str, int]
) -> tuple[dict[str, int], int, bool]:
    expected_question_ids = QUESTIONNAIRE_QUESTION_IDS[questionnaire_code]
    provided_question_ids = set(answers.keys())
    expected_set = set(expected_question_ids)

    if provided_question_ids != expected_set:
        expected = ", ".join(expected_question_ids)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"answers must include exactly: {expected}",
        )

    normalized_answers: dict[str, int] = {}
    total_score = 0
    for question_id in expected_question_ids:
        value = answers[question_id]
        if value < 0 or value > 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{question_id} must be between 0 and 3",
            )
        normalized_answers[question_id] = value
        total_score += value

    has_safety_signal = (
        questionnaire_code == QuestionnaireCode.phq9.value and normalized_answers["q9"] > 0
    )
    return normalized_answers, total_score, has_safety_signal


def _to_assignment_item(assignment: QuestionnaireAssignment) -> QuestionnaireAssignmentItem:
    response = assignment.response
    return QuestionnaireAssignmentItem(
        id=assignment.id,
        questionnaire_code=assignment.questionnaire_code,  # type: ignore[arg-type]
        status=assignment.status,  # type: ignore[arg-type]
        assigned_at=_normalize_timestamp(assignment.assigned_at),
        completed_at=(
            _normalize_timestamp(assignment.completed_at) if assignment.completed_at else None
        ),
        total_score=response.total_score if response else None,
        has_safety_signal=response.has_safety_signal if response else None,
    )


@router.get(
    "/patients/{patient_id}/questionnaires",
    response_model=QuestionnaireAssignmentListResponse,
)
async def list_patient_questionnaires(
    patient_id: UUID,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> QuestionnaireAssignmentListResponse:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    result = await db.execute(
        select(QuestionnaireAssignment)
        .options(selectinload(QuestionnaireAssignment.response))
        .where(
            QuestionnaireAssignment.patient_user_id == patient_id,
            QuestionnaireAssignment.doctor_user_id == doctor.id,
        )
        .order_by(QuestionnaireAssignment.assigned_at.desc())
    )
    return QuestionnaireAssignmentListResponse(
        items=[_to_assignment_item(item) for item in result.scalars().all()]
    )


@router.post(
    "/patients/{patient_id}/questionnaires",
    response_model=QuestionnaireAssignmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient_questionnaire_assignment(
    patient_id: UUID,
    body: CreateQuestionnaireAssignmentRequest,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> QuestionnaireAssignmentOut:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    assignment = QuestionnaireAssignment(
        patient_user_id=patient_id,
        doctor_user_id=doctor.id,
        questionnaire_code=body.questionnaire_code,
        status=QuestionnaireAssignmentStatus.assigned.value,
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return QuestionnaireAssignmentOut.model_validate(assignment)


@router.get("/questionnaires/pending", response_model=PendingQuestionnaireListResponse)
async def list_pending_questionnaires(
    patient: Annotated[User, Depends(require_role(Role.patient))],
    db: AsyncSession = Depends(get_db),
) -> PendingQuestionnaireListResponse:
    result = await db.execute(
        select(QuestionnaireAssignment)
        .where(
            QuestionnaireAssignment.patient_user_id == patient.id,
            QuestionnaireAssignment.status == QuestionnaireAssignmentStatus.assigned.value,
        )
        .order_by(QuestionnaireAssignment.assigned_at.desc())
    )
    items = [
        PendingQuestionnaireItem(
            id=item.id,
            questionnaire_code=item.questionnaire_code,  # type: ignore[arg-type]
            status="assigned",
            assigned_at=_normalize_timestamp(item.assigned_at),
        )
        for item in result.scalars().all()
    ]
    return PendingQuestionnaireListResponse(items=items)


@router.post(
    "/questionnaires/{assignment_id}/submit",
    response_model=QuestionnaireSubmissionResult,
)
async def submit_questionnaire(
    assignment_id: UUID,
    body: SubmitQuestionnaireRequest,
    patient: Annotated[User, Depends(require_role(Role.patient))],
    db: AsyncSession = Depends(get_db),
) -> QuestionnaireSubmissionResult:
    assignment_result = await db.execute(
        select(QuestionnaireAssignment).where(
            QuestionnaireAssignment.id == assignment_id,
            QuestionnaireAssignment.patient_user_id == patient.id,
        )
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire assignment not found",
        )
    if assignment.status != QuestionnaireAssignmentStatus.assigned.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Questionnaire has already been submitted",
        )

    normalized_answers, total_score, has_safety_signal = _score_answers(
        assignment.questionnaire_code,
        body.answers,
    )

    submitted_at = datetime.now(UTC)
    response = QuestionnaireResponse(
        assignment_id=assignment.id,
        patient_user_id=patient.id,
        questionnaire_code=assignment.questionnaire_code,
        answers=normalized_answers,
        total_score=total_score,
        has_safety_signal=has_safety_signal,
        submitted_at=submitted_at,
    )
    assignment.status = QuestionnaireAssignmentStatus.completed.value
    assignment.completed_at = submitted_at
    db.add(response)
    await db.flush()
    await db.refresh(response)

    return QuestionnaireSubmissionResult.model_validate(response)
