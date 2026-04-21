from __future__ import annotations

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.adherence_log import AdherenceLog
from app.db.models.medication import Medication
from app.db.models.questionnaire_assignment import (
    QuestionnaireAssignment,
    QuestionnaireAssignmentStatus,
    QuestionnaireCode,
)
from app.db.models.questionnaire_response import QuestionnaireResponse
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


async def test_doctor_gets_recent_patient_summary_with_safety_flags(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_headers: dict[str, str],
    doctor_user: User,
    patient_user: User,
) -> None:
    medication = await _create_medication(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
    )

    assignment = QuestionnaireAssignment(
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        questionnaire_code=QuestionnaireCode.phq9.value,
        status=QuestionnaireAssignmentStatus.completed.value,
        completed_at=datetime.now(UTC),
    )
    db_session.add(assignment)
    await db_session.flush()

    db_session.add(
        QuestionnaireResponse(
            assignment_id=assignment.id,
            patient_user_id=patient_user.id,
            questionnaire_code=QuestionnaireCode.phq9.value,
            answers={f"q{i}": (1 if i in [1, 9] else 0) for i in range(1, 10)},
            total_score=2,
            has_safety_signal=True,
            submitted_at=datetime.now(UTC) - timedelta(hours=2),
        )
    )
    db_session.add(
        AdherenceLog(
            medication_id=medication.id,
            patient_user_id=patient_user.id,
            status="modified",
            deviation_note="Half dose",
            logged_at=datetime.now(UTC) - timedelta(hours=1),
        )
    )
    db_session.add(
        SideEffectReport(
            patient_user_id=patient_user.id,
            doctor_user_id=doctor_user.id,
            medication_id=medication.id,
            severity="severe",
            symptom="Intense dizziness",
            note="Started after morning dose",
            reported_at=datetime.now(UTC),
        )
    )
    await db_session.commit()

    response = await client.get(
        f"/api/v1/patients/{patient_user.id}/summary",
        headers=doctor_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["patient_id"] == str(patient_user.id)

    assert len(payload["questionnaires"]) == 1
    assert payload["questionnaires"][0]["questionnaire_code"] == "PHQ-9"
    assert payload["questionnaires"][0]["has_safety_signal"] is True

    assert len(payload["adherence"]) == 1
    assert payload["adherence"][0]["status"] == "modified"
    assert payload["adherence"][0]["medication_id"] == str(medication.id)

    assert len(payload["side_effects"]) == 1
    assert payload["side_effects"][0]["severity"] == "severe"
    assert payload["side_effects"][0]["symptom"] == "Intense dizziness"

    assert payload["safety_flags"] == [
        {
            "source": "questionnaire",
            "level": "critical",
            "code": "questionnaire_safety_signal",
        },
        {
            "source": "side_effect",
            "level": "warning",
            "code": "severe_side_effect_reported",
        },
    ]


async def test_doctor_cannot_get_summary_for_unassigned_patient(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    other_patient_user: User,
) -> None:
    response = await client.get(
        f"/api/v1/patients/{other_patient_user.id}/summary",
        headers=doctor_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"
