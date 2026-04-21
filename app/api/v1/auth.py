from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import create_access_token, get_current_user, verify_password
from app.db.models.patient_profile import PatientProfile
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LogoutResponse, TokenResponse
from app.schemas.users import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(
        select(User)
        .options(selectinload(User.patient_profile))
        .where(User.email == body.email.strip().lower())
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    if user.patient_profile is not None and not user.patient_profile.is_active_with_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    patient_profile: PatientProfile | None = None
    if user.role.value == "patient":
        result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == user.id))
        patient_profile = result.scalar_one_or_none()

    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role.value,
        is_active=(
            user.is_active
            and (patient_profile.is_active_with_doctor if patient_profile else True)
        ),
        onboarding_status=patient_profile.onboarding_status if patient_profile else None,
        must_change_password=patient_profile.must_change_password if patient_profile else None,
        doctor_user_id=patient_profile.doctor_user_id if patient_profile else None,
    )


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(_user: Annotated[User, Depends(get_current_user)]) -> LogoutResponse:
    # Stateless logout. Add Redis token blacklist here when needed.
    return LogoutResponse()
