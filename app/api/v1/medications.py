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
from app.db.models.user import User, UserRole
from app.db.session import get_db
from app.schemas.medications import (
    AdherenceLogItem,
    AdherenceLogListResponse,
    CreateAdherenceLogRequest,
    CreateMedicationRequest,
    MedicationListResponse,
    MedicationOut,
)

router = APIRouter(tags=["medications"])


def _normalize_logged_at(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _to_adherence_log_item(log: AdherenceLog) -> AdherenceLogItem:
    return AdherenceLogItem(
        id=log.id,
        medication_id=log.medication_id,
        status=log.status,  # type: ignore[arg-type]
        deviation_note=log.deviation_note,
        logged_at=_normalize_logged_at(log.logged_at),
    )


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


@router.get("/patients/{patient_id}/medications", response_model=MedicationListResponse)
async def list_patient_medications(
    patient_id: UUID,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> MedicationListResponse:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    result = await db.execute(
        select(Medication)
        .where(
            Medication.patient_user_id == patient_id,
            Medication.doctor_user_id == doctor.id,
            Medication.is_active.is_(True),
        )
        .order_by(Medication.created_at.desc())
    )
    return MedicationListResponse(items=list(result.scalars().all()))


@router.post(
    "/patients/{patient_id}/medications",
    response_model=MedicationOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient_medication(
    patient_id: UUID,
    body: CreateMedicationRequest,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> MedicationOut:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    medication = Medication(
        patient_user_id=patient_id,
        doctor_user_id=doctor.id,
        name=body.name.strip(),
        dosage_instructions=body.dosage_instructions.strip(),
        is_active=body.is_active,
    )
    db.add(medication)
    await db.flush()
    await db.refresh(medication)
    return MedicationOut.model_validate(medication)


@router.get("/medications/current", response_model=MedicationListResponse)
async def list_current_medications(
    patient: Annotated[User, Depends(require_role(Role.patient))],
    db: AsyncSession = Depends(get_db),
) -> MedicationListResponse:
    result = await db.execute(
        select(Medication)
        .where(
            Medication.patient_user_id == patient.id,
            Medication.is_active.is_(True),
        )
        .order_by(Medication.created_at.desc())
    )
    return MedicationListResponse(items=list(result.scalars().all()))


@router.post(
    "/medications/{medication_id}/adherence",
    response_model=AdherenceLogItem,
    status_code=status.HTTP_201_CREATED,
)
async def create_adherence_log(
    medication_id: UUID,
    body: CreateAdherenceLogRequest,
    patient: Annotated[User, Depends(require_role(Role.patient))],
    db: AsyncSession = Depends(get_db),
) -> AdherenceLogItem:
    result = await db.execute(
        select(Medication).where(
            Medication.id == medication_id,
            Medication.patient_user_id == patient.id,
            Medication.is_active.is_(True),
        )
    )
    medication = result.scalar_one_or_none()
    if medication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    deviation_note = body.deviation_note.strip() if body.deviation_note else None
    logged_at = body.logged_at or datetime.now(UTC)

    adherence_log = AdherenceLog(
        medication_id=medication.id,
        patient_user_id=patient.id,
        status=body.status,
        deviation_note=deviation_note or None,
        logged_at=logged_at,
    )
    db.add(adherence_log)
    await db.flush()
    await db.refresh(adherence_log)
    return _to_adherence_log_item(adherence_log)


@router.get("/patients/{patient_id}/adherence", response_model=AdherenceLogListResponse)
async def list_patient_adherence_logs(
    patient_id: UUID,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> AdherenceLogListResponse:
    await _get_assigned_patient_or_404(db, doctor.id, patient_id)

    result = await db.execute(
        select(AdherenceLog)
        .join(Medication, Medication.id == AdherenceLog.medication_id)
        .where(
            AdherenceLog.patient_user_id == patient_id,
            Medication.doctor_user_id == doctor.id,
        )
        .order_by(AdherenceLog.logged_at.desc(), AdherenceLog.created_at.desc())
    )
    return AdherenceLogListResponse(
        items=[_to_adherence_log_item(item) for item in result.scalars()]
    )
