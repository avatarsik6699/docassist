from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password
from app.db.models.doctor_profile import DoctorProfile
from app.db.models.patient_profile import OnboardingStatus, PatientProfile
from app.db.models.user import User, UserRole


@pytest.fixture()
async def doctor_user(db_session: AsyncSession) -> User:
    user = User(
        email=f"doctor_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("changeme123"),
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(DoctorProfile(user_id=user.id))
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
def doctor_headers(doctor_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(doctor_user.id), "role": doctor_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def other_doctor_user(db_session: AsyncSession) -> User:
    user = User(
        email=f"doctor_other_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("changeme123"),
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(DoctorProfile(user_id=user.id))
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
async def patient_user(db_session: AsyncSession, doctor_user: User) -> User:
    user = User(
        email=f"patient_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(
        PatientProfile(
            user_id=user.id,
            doctor_user_id=doctor_user.id,
            onboarding_status=OnboardingStatus.pending.value,
            must_change_password=True,
            is_active_with_doctor=True,
        )
    )
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
def patient_headers(patient_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(patient_user.id), "role": patient_user.role.value})
    return {"Authorization": f"Bearer {token}"}


async def test_doctor_can_list_only_assigned_patients(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    doctor_headers: dict[str, str],
    other_doctor_user: User,
) -> None:
    visible_patient = User(
        email=f"visible_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=True,
    )
    hidden_patient = User(
        email=f"hidden_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=True,
    )
    db_session.add_all([visible_patient, hidden_patient])
    await db_session.flush()
    db_session.add_all(
        [
            PatientProfile(
                user_id=visible_patient.id,
                doctor_user_id=doctor_user.id,
                onboarding_status=OnboardingStatus.pending.value,
                must_change_password=True,
                is_active_with_doctor=True,
            ),
            PatientProfile(
                user_id=hidden_patient.id,
                doctor_user_id=other_doctor_user.id,
                onboarding_status=OnboardingStatus.completed.value,
                must_change_password=False,
                is_active_with_doctor=True,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get("/api/v1/patients", headers=doctor_headers)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(visible_patient.id),
                "email": visible_patient.email,
                "is_active": True,
                "onboarding_status": "pending",
            }
        ]
    }


async def test_doctor_can_create_patient_account(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    doctor_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/patients",
        headers=doctor_headers,
        json={"email": "new.patient@example.com"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new.patient@example.com"
    assert data["doctor_user_id"] == str(doctor_user.id)
    assert data["onboarding_status"] == "pending"
    assert len(data["temporary_password"]) >= 12

    created_user = await db_session.get(User, UUID(data["id"]))
    assert created_user is not None
    assert created_user.role == UserRole.patient

    profile = await db_session.get(PatientProfile, created_user.id)
    assert profile is not None
    assert profile.doctor_user_id == doctor_user.id
    assert profile.must_change_password is True


async def test_doctor_cannot_create_patient_owned_by_other_doctor(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_headers: dict[str, str],
    other_doctor_user: User,
) -> None:
    patient = User(
        email="shared.patient@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=True,
    )
    db_session.add(patient)
    await db_session.flush()
    db_session.add(
        PatientProfile(
            user_id=patient.id,
            doctor_user_id=other_doctor_user.id,
            onboarding_status=OnboardingStatus.pending.value,
            must_change_password=True,
            is_active_with_doctor=True,
        )
    )
    await db_session.commit()

    response = await client.post(
        "/api/v1/patients",
        headers=doctor_headers,
        json={"email": "shared.patient@example.com"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Patient is already assigned to another doctor"


async def test_doctor_can_activate_own_inactive_patient(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_headers: dict[str, str],
    patient_user: User,
) -> None:
    patient_user.is_active = False
    profile = await db_session.get(PatientProfile, patient_user.id)
    assert profile is not None
    profile.is_active_with_doctor = False
    await db_session.commit()

    response = await client.post(
        f"/api/v1/patients/{patient_user.id}/activate",
        headers=doctor_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(patient_user.id),
        "is_active": True,
        "onboarding_status": "pending",
    }


async def test_doctor_cannot_activate_other_doctors_patient(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_headers: dict[str, str],
    other_doctor_user: User,
) -> None:
    patient = User(
        email=f"other_patient_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=False,
    )
    db_session.add(patient)
    await db_session.flush()
    db_session.add(
        PatientProfile(
            user_id=patient.id,
            doctor_user_id=other_doctor_user.id,
            onboarding_status=OnboardingStatus.pending.value,
            must_change_password=True,
            is_active_with_doctor=False,
        )
    )
    await db_session.commit()

    response = await client.post(
        f"/api/v1/patients/{patient.id}/activate",
        headers=doctor_headers,
    )

    assert response.status_code == 404


async def test_patient_can_complete_setup_account(
    client: AsyncClient,
    db_session: AsyncSession,
    patient_user: User,
    patient_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/patients/setup-account",
        headers=patient_headers,
        json={"new_password": "permanent123"},
    )

    assert response.status_code == 200
    assert response.json()["onboarding_status"] == "completed"
    assert response.json()["must_change_password"] is False

    profile = await db_session.get(PatientProfile, patient_user.id)
    assert profile is not None
    assert profile.onboarding_status == "completed"
    assert profile.must_change_password is False


async def test_patient_login_is_blocked_when_inactive_with_doctor(
    client: AsyncClient,
    db_session: AsyncSession,
    patient_user: User,
) -> None:
    profile = await db_session.get(PatientProfile, patient_user.id)
    assert profile is not None
    profile.is_active_with_doctor = False
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": patient_user.email, "password": "temporary123"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is disabled"
