from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import Role, generate_temporary_password, hash_password, require_role
from app.db.models.patient_profile import OnboardingStatus, PatientProfile
from app.db.models.user import User, UserRole
from app.db.session import get_db
from app.schemas.profiles import (
    ActivatePatientResponse,
    CreatePatientRequest,
    CreatePatientResponse,
    PatientRosterItem,
    PatientRosterResponse,
    SetupAccountRequest,
)
from app.schemas.users import UserOut

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=PatientRosterResponse)
async def list_patients(
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> PatientRosterResponse:
    result = await db.execute(
        select(User, PatientProfile)
        .join(PatientProfile, PatientProfile.user_id == User.id)
        .where(
            User.role == UserRole.patient,
            PatientProfile.doctor_user_id == doctor.id,
        )
        .order_by(User.email.asc())
    )

    items = [
        PatientRosterItem(
            id=user.id,
            email=user.email,
            is_active=user.is_active and profile.is_active_with_doctor,
            onboarding_status=profile.onboarding_status,
        )
        for user, profile in result.all()
    ]
    return PatientRosterResponse(items=items)


@router.post("", response_model=CreatePatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    body: CreatePatientRequest,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> CreatePatientResponse:
    existing_result = await db.execute(
        select(User)
        .options(selectinload(User.patient_profile))
        .where(User.email == body.email.strip().lower())
    )
    existing_user = existing_result.scalar_one_or_none()

    if existing_user is not None:
        if existing_user.role != UserRole.patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already belongs to a non-patient account",
            )
        if existing_user.patient_profile is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient account is missing its profile",
            )
        if existing_user.patient_profile.doctor_user_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient is already assigned to another doctor",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already exists for this doctor",
        )

    temporary_password = generate_temporary_password()
    patient = User(
        email=body.email.strip().lower(),
        hashed_password=hash_password(temporary_password),
        role=UserRole.patient,
        is_active=True,
    )
    db.add(patient)
    await db.flush()

    patient_profile = PatientProfile(
        user_id=patient.id,
        doctor_user_id=doctor.id,
        onboarding_status=OnboardingStatus.pending.value,
        must_change_password=True,
        is_active_with_doctor=True,
    )
    db.add(patient_profile)

    return CreatePatientResponse(
        id=patient.id,
        email=patient.email,
        doctor_user_id=doctor.id,
        onboarding_status="pending",
        temporary_password=temporary_password,
    )


@router.post("/{patient_id}/activate", response_model=ActivatePatientResponse)
async def activate_patient(
    patient_id: UUID,
    doctor: Annotated[User, Depends(require_role(Role.doctor))],
    db: AsyncSession = Depends(get_db),
) -> ActivatePatientResponse:
    result = await db.execute(
        select(User, PatientProfile)
        .join(PatientProfile, PatientProfile.user_id == User.id)
        .where(
            User.id == patient_id,
            User.role == UserRole.patient,
            PatientProfile.doctor_user_id == doctor.id,
        )
    )
    row = result.one_or_none()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    patient, profile = row
    patient.is_active = True
    profile.is_active_with_doctor = True

    return ActivatePatientResponse(
        id=patient.id,
        is_active=True,
        onboarding_status=profile.onboarding_status,
    )


@router.post("/setup-account", response_model=UserOut)
async def setup_account(
    body: SetupAccountRequest,
    patient: Annotated[User, Depends(require_role(Role.patient))],
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == patient.id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    patient.hashed_password = hash_password(body.new_password)
    profile.must_change_password = False
    profile.onboarding_status = OnboardingStatus.completed.value

    return UserOut(
        id=patient.id,
        email=patient.email,
        role=patient.role.value,
        is_active=patient.is_active and profile.is_active_with_doctor,
        onboarding_status=profile.onboarding_status,
        must_change_password=profile.must_change_password,
        doctor_user_id=profile.doctor_user_id,
    )
