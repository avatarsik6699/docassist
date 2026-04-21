from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.db.models.adherence_log import AdherenceLog
from app.db.models.medication import Medication
from app.db.models.patient_profile import OnboardingStatus, PatientProfile
from app.db.models.user import User, UserRole


async def _create_patient(
    db_session: AsyncSession,
    doctor_user: User,
    *,
    email_prefix: str = "patient",
) -> User:
    patient = User(
        email=f"{email_prefix}_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=True,
    )
    db_session.add(patient)
    await db_session.flush()
    db_session.add(
        PatientProfile(
            user_id=patient.id,
            doctor_user_id=doctor_user.id,
            onboarding_status=OnboardingStatus.completed.value,
            must_change_password=False,
            is_active_with_doctor=True,
        )
    )
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


async def _create_medication(
    db_session: AsyncSession,
    *,
    patient_user_id,
    doctor_user_id,
    name: str = "Sertraline",
    dosage_instructions: str = "50 mg once daily",
    is_active: bool = True,
) -> Medication:
    medication = Medication(
        patient_user_id=patient_user_id,
        doctor_user_id=doctor_user_id,
        name=name,
        dosage_instructions=dosage_instructions,
        is_active=is_active,
    )
    db_session.add(medication)
    await db_session.commit()
    await db_session.refresh(medication)
    return medication


async def test_doctor_can_create_and_list_patient_medications(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    doctor_headers: dict[str, str],
    patient_user: User,
) -> None:
    archived = await _create_medication(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        name="Old medication",
        is_active=False,
    )

    create_response = await client.post(
        f"/api/v1/patients/{patient_user.id}/medications",
        headers=doctor_headers,
        json={
            "name": "Sertraline",
            "dosage_instructions": "50 mg once daily",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["patient_user_id"] == str(patient_user.id)
    assert created["doctor_user_id"] == str(doctor_user.id)
    assert created["name"] == "Sertraline"
    assert created["is_active"] is True

    list_response = await client.get(
        f"/api/v1/patients/{patient_user.id}/medications",
        headers=doctor_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "id": created["id"],
                "name": "Sertraline",
                "dosage_instructions": "50 mg once daily",
                "is_active": True,
            }
        ]
    }
    assert archived.id != created["id"]


async def test_doctor_cannot_manage_other_doctors_patient_medications(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_headers: dict[str, str],
    other_doctor_user: User,
) -> None:
    other_patient = await _create_patient(
        db_session,
        other_doctor_user,
        email_prefix="other_patient",
    )

    response = await client.post(
        f"/api/v1/patients/{other_patient.id}/medications",
        headers=doctor_headers,
        json={
            "name": "Sertraline",
            "dosage_instructions": "50 mg once daily",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


async def test_patient_can_list_current_medications(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_user: User,
    patient_headers: dict[str, str],
) -> None:
    active = await _create_medication(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        name="Metformin",
        dosage_instructions="500 mg with breakfast",
    )
    await _create_medication(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        name="Paused medication",
        dosage_instructions="skip",
        is_active=False,
    )

    response = await client.get("/api/v1/medications/current", headers=patient_headers)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(active.id),
                "name": "Metformin",
                "dosage_instructions": "500 mg with breakfast",
                "is_active": True,
            }
        ]
    }


async def test_patient_can_log_adherence_for_own_active_medication(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_user: User,
    patient_headers: dict[str, str],
) -> None:
    medication = await _create_medication(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
    )
    logged_at = datetime.now(UTC).replace(microsecond=0)

    response = await client.post(
        f"/api/v1/medications/{medication.id}/adherence",
        headers=patient_headers,
        json={
            "status": "modified",
            "deviation_note": "  Took half dose after nausea  ",
            "logged_at": logged_at.isoformat(),
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload == {
        "id": payload["id"],
        "medication_id": str(medication.id),
        "status": "modified",
        "deviation_note": "Took half dose after nausea",
        "logged_at": logged_at.isoformat().replace("+00:00", "Z"),
    }

    stored_log = await db_session.get(AdherenceLog, UUID(payload["id"]))
    assert stored_log is not None
    assert stored_log.patient_user_id == patient_user.id


async def test_patient_cannot_log_adherence_for_other_patients_medication(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_headers: dict[str, str],
) -> None:
    other_patient = await _create_patient(db_session, doctor_user, email_prefix="other_owned")
    medication = await _create_medication(
        db_session,
        patient_user_id=other_patient.id,
        doctor_user_id=doctor_user.id,
    )

    response = await client.post(
        f"/api/v1/medications/{medication.id}/adherence",
        headers=patient_headers,
        json={"status": "taken"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Medication not found"


async def test_doctor_can_review_patient_adherence_history(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    doctor_headers: dict[str, str],
    patient_user: User,
) -> None:
    medication = await _create_medication(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
    )
    older = datetime.now(UTC) - timedelta(days=1)
    newer = datetime.now(UTC)
    db_session.add_all(
        [
            AdherenceLog(
                medication_id=medication.id,
                patient_user_id=patient_user.id,
                status="missed",
                deviation_note="Forgot evening dose",
                logged_at=older,
            ),
            AdherenceLog(
                medication_id=medication.id,
                patient_user_id=patient_user.id,
                status="taken",
                deviation_note=None,
                logged_at=newer,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(
        f"/api/v1/patients/{patient_user.id}/adherence",
        headers=doctor_headers,
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["status"] for item in items] == ["taken", "missed"]
    assert items[0]["medication_id"] == str(medication.id)
    assert items[1]["deviation_note"] == "Forgot evening dose"
