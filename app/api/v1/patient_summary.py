from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import Role, require_role
from app.db.models.adherence_log import AdherenceLog
from app.db.models.medication import Medication
from app.db.models.patient_profile import PatientProfile
from app.db.models.questionnaire_assignment import QuestionnaireAssignment
from app.db.models.questionnaire_response import QuestionnaireResponse
from app.db.models.side_effect_report import SideEffectReport
from app.db.models.user import User, UserRole
from app.db.session import get_db
from app.schemas.patient_summary import (
    PatientAdherenceSummaryItem,
    PatientQuestionnaireSummaryItem,
    PatientSafetyFlag,
    PatientSideEffectSummaryItem,
    PatientSummaryResponse,
)

router = APIRouter(tags=["patient-summary"])

MAX_ITEMS = 10


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


@router.get(
    "/patients/{patient_id}/summary",
    response_model=PatientSummaryResponse,
)
async def get_patient_summary(
    patient_id: UUID,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> PatientSummaryResponse:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    questionnaire_result = await db.execute(
        select(QuestionnaireAssignment, QuestionnaireResponse)
        .join(
            QuestionnaireResponse,
            QuestionnaireResponse.assignment_id == QuestionnaireAssignment.id,
        )
        .where(
            QuestionnaireAssignment.patient_user_id == patient_id,
            QuestionnaireAssignment.doctor_user_id == doctor.id,
        )
        .order_by(QuestionnaireResponse.submitted_at.desc())
        .limit(MAX_ITEMS)
    )

    questionnaires = [
        PatientQuestionnaireSummaryItem(
            assignment_id=assignment.id,
            questionnaire_code=assignment.questionnaire_code,  # type: ignore[arg-type]
            total_score=response.total_score,
            has_safety_signal=response.has_safety_signal,
            submitted_at=_normalize_timestamp(response.submitted_at),
        )
        for assignment, response in questionnaire_result.all()
    ]

    adherence_result = await db.execute(
        select(AdherenceLog)
        .join(Medication, Medication.id == AdherenceLog.medication_id)
        .where(
            AdherenceLog.patient_user_id == patient_id,
            Medication.doctor_user_id == doctor.id,
        )
        .order_by(AdherenceLog.logged_at.desc(), AdherenceLog.created_at.desc())
        .limit(MAX_ITEMS)
    )
    adherence = [
        PatientAdherenceSummaryItem(
            id=item.id,
            medication_id=item.medication_id,
            status=item.status,  # type: ignore[arg-type]
            logged_at=_normalize_timestamp(item.logged_at),
        )
        for item in adherence_result.scalars().all()
    ]

    side_effect_result = await db.execute(
        select(SideEffectReport)
        .where(
            SideEffectReport.patient_user_id == patient_id,
            SideEffectReport.doctor_user_id == doctor.id,
        )
        .order_by(SideEffectReport.reported_at.desc(), SideEffectReport.created_at.desc())
        .limit(MAX_ITEMS)
    )
    side_effects = [
        PatientSideEffectSummaryItem(
            id=item.id,
            severity=item.severity,  # type: ignore[arg-type]
            symptom=item.symptom,
            reported_at=_normalize_timestamp(item.reported_at),
        )
        for item in side_effect_result.scalars().all()
    ]

    seen_flags: set[tuple[str, str, str]] = set()
    flags: list[PatientSafetyFlag] = []

    for questionnaire in questionnaires:
        if not questionnaire.has_safety_signal:
            continue
        key = ("questionnaire", "critical", "questionnaire_safety_signal")
        if key not in seen_flags:
            seen_flags.add(key)
            flags.append(
                PatientSafetyFlag(
                    source="questionnaire",
                    level="critical",
                    code="questionnaire_safety_signal",
                )
            )

    if any(side_effect.severity == "severe" for side_effect in side_effects):
        key = ("side_effect", "warning", "severe_side_effect_reported")
        if key not in seen_flags:
            flags.append(
                PatientSafetyFlag(
                    source="side_effect",
                    level="warning",
                    code="severe_side_effect_reported",
                )
            )

    return PatientSummaryResponse(
        patient_id=patient_id,
        questionnaires=questionnaires,
        adherence=adherence,
        side_effects=side_effects,
        safety_flags=flags,
    )
