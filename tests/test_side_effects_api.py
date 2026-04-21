from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.medication import Medication
from app.db.models.side_effect_report import SideEffectReport
from app.db.models.user import User


async def _create_medication(
    db_session: AsyncSession,
    *,
    patient_user_id,
    doctor_user_id,
    name: str = "Sertraline",
) -> Medication:
    medication = Medication(
        patient_user_id=patient_user_id,
        doctor_user_id=doctor_user_id,
        name=name,
        dosage_instructions="50 mg once daily",
        is_active=True,
    )
    db_session.add(medication)
    await db_session.commit()
    await db_session.refresh(medication)
    return medication


async def test_patient_can_submit_side_effect_report(
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
    reported_at = datetime.now(UTC).replace(microsecond=0)

    response = await client.post(
        "/api/v1/side-effects",
        headers=patient_headers,
        json={
            "severity": "severe",
            "symptom": "  Persistent nausea  ",
            "note": "  Started yesterday after evening dose  ",
            "medication_id": str(medication.id),
            "reported_at": reported_at.isoformat(),
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["patient_user_id"] == str(patient_user.id)
    assert payload["doctor_user_id"] == str(doctor_user.id)
    assert payload["medication_id"] == str(medication.id)
    assert payload["severity"] == "severe"
    assert payload["symptom"] == "Persistent nausea"
    assert payload["note"] == "Started yesterday after evening dose"
    assert payload["reported_at"].startswith(reported_at.isoformat().replace("+00:00", ""))

    stored = await db_session.get(SideEffectReport, UUID(payload["id"]))
    assert stored is not None


async def test_patient_cannot_submit_side_effect_for_other_patients_medication(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_user: User,
    other_patient_user: User,
    patient_headers: dict[str, str],
) -> None:
    medication = await _create_medication(
        db_session,
        patient_user_id=other_patient_user.id,
        doctor_user_id=doctor_user.id,
        name="Escitalopram",
    )

    response = await client.post(
        "/api/v1/side-effects",
        headers=patient_headers,
        json={
            "severity": "moderate",
            "symptom": "Headache",
            "medication_id": str(medication.id),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Medication not found"


async def test_doctor_can_list_side_effect_history_for_assigned_patient(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_headers: dict[str, str],
    doctor_user: User,
    patient_user: User,
) -> None:
    db_session.add_all(
        [
            SideEffectReport(
                patient_user_id=patient_user.id,
                doctor_user_id=doctor_user.id,
                severity="mild",
                symptom="Dry mouth",
                note=None,
                reported_at=datetime.now(UTC) - timedelta(hours=2),
            ),
            SideEffectReport(
                patient_user_id=patient_user.id,
                doctor_user_id=doctor_user.id,
                severity="severe",
                symptom="Worsening insomnia",
                note="Could not sleep",
                reported_at=datetime.now(UTC) - timedelta(hours=1),
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(
        f"/api/v1/patients/{patient_user.id}/side-effects",
        headers=doctor_headers,
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2
    assert items[0]["severity"] == "severe"
    assert items[0]["symptom"] == "Worsening insomnia"


async def test_doctor_cannot_list_side_effect_history_for_unassigned_patient(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    other_patient_user: User,
) -> None:
    response = await client.get(
        f"/api/v1/patients/{other_patient_user.id}/side-effects",
        headers=doctor_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"
