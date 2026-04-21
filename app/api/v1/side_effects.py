from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import Role, require_role
from app.db.models.medication import Medication
from app.db.models.patient_profile import PatientProfile
from app.db.models.side_effect_report import SideEffectReport
from app.db.models.user import User, UserRole
from app.db.session import get_db
from app.schemas.side_effects import (
    CreateSideEffectReportRequest,
    SideEffectReportItem,
    SideEffectReportListResponse,
    SideEffectReportOut,
)

router = APIRouter(tags=["side-effects"])


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


@router.post(
    "/side-effects",
    response_model=SideEffectReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_side_effect_report(
    body: CreateSideEffectReportRequest,
    patient: Annotated[User, Depends(require_role(Role.patient))],
    db: AsyncSession = Depends(get_db),
) -> SideEffectReportOut:
    profile_result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == patient.id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    medication_id: UUID | None = None
    if body.medication_id is not None:
        medication_result = await db.execute(
            select(Medication).where(
                Medication.id == body.medication_id,
                Medication.patient_user_id == patient.id,
                Medication.doctor_user_id == profile.doctor_user_id,
            )
        )
        medication = medication_result.scalar_one_or_none()
        if medication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found",
            )
        medication_id = medication.id

    note = body.note.strip() if body.note else None
    report = SideEffectReport(
        patient_user_id=patient.id,
        doctor_user_id=profile.doctor_user_id,
        medication_id=medication_id,
        severity=body.severity,
        symptom=body.symptom.strip(),
        note=note or None,
        reported_at=body.reported_at or datetime.now(UTC),
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return SideEffectReportOut.model_validate(report)


@router.get(
    "/patients/{patient_id}/side-effects",
    response_model=SideEffectReportListResponse,
)
async def list_patient_side_effects(
    patient_id: UUID,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> SideEffectReportListResponse:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    result = await db.execute(
        select(SideEffectReport)
        .where(
            SideEffectReport.patient_user_id == patient_id,
            SideEffectReport.doctor_user_id == doctor.id,
        )
        .order_by(SideEffectReport.reported_at.desc(), SideEffectReport.created_at.desc())
    )
    return SideEffectReportListResponse(
        items=[
            SideEffectReportItem(
                id=item.id,
                severity=item.severity,  # type: ignore[arg-type]
                symptom=item.symptom,
                note=item.note,
                reported_at=_normalize_timestamp(item.reported_at),
            )
            for item in result.scalars().all()
        ]
    )
