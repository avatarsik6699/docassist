from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.db.models.patient_profile import OnboardingStatus, PatientProfile
from app.db.models.questionnaire_assignment import (
    QuestionnaireAssignment,
    QuestionnaireAssignmentStatus,
    QuestionnaireCode,
)
from app.db.models.questionnaire_response import QuestionnaireResponse
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


async def _create_assignment(
    db_session: AsyncSession,
    *,
    patient_user_id: UUID,
    doctor_user_id: UUID,
    questionnaire_code: str = QuestionnaireCode.phq9.value,
) -> QuestionnaireAssignment:
    assignment = QuestionnaireAssignment(
        patient_user_id=patient_user_id,
        doctor_user_id=doctor_user_id,
        questionnaire_code=questionnaire_code,
        status=QuestionnaireAssignmentStatus.assigned.value,
    )
    db_session.add(assignment)
    await db_session.commit()
    await db_session.refresh(assignment)
    return assignment


async def test_doctor_can_assign_and_list_patient_questionnaires(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    doctor_user: User,
    patient_user: User,
) -> None:
    create_response = await client.post(
        f"/api/v1/patients/{patient_user.id}/questionnaires",
        headers=doctor_headers,
        json={"questionnaire_code": "PHQ-9"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["patient_user_id"] == str(patient_user.id)
    assert created["doctor_user_id"] == str(doctor_user.id)
    assert created["questionnaire_code"] == "PHQ-9"
    assert created["status"] == "assigned"

    list_response = await client.get(
        f"/api/v1/patients/{patient_user.id}/questionnaires",
        headers=doctor_headers,
    )
    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["items"][0]["id"] == created["id"]
    assert payload["items"][0]["status"] == "assigned"
    assert payload["items"][0]["completed_at"] is None
    assert payload["items"][0]["total_score"] is None


async def test_doctor_cannot_assign_questionnaires_to_other_doctors_patient(
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
        f"/api/v1/patients/{other_patient.id}/questionnaires",
        headers=doctor_headers,
        json={"questionnaire_code": "GAD-7"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


async def test_patient_can_list_pending_questionnaires(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_headers: dict[str, str],
    patient_user: User,
) -> None:
    await _create_assignment(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        questionnaire_code=QuestionnaireCode.gad7.value,
    )

    response = await client.get("/api/v1/questionnaires/pending", headers=patient_headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["questionnaire_code"] == "GAD-7"
    assert payload["items"][0]["status"] == "assigned"


async def test_patient_can_submit_phq9_and_trigger_safety_signal(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_headers: dict[str, str],
    patient_user: User,
) -> None:
    assignment = await _create_assignment(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        questionnaire_code=QuestionnaireCode.phq9.value,
    )

    response = await client.post(
        f"/api/v1/questionnaires/{assignment.id}/submit",
        headers=patient_headers,
        json={
            "answers": {
                "q1": 0,
                "q2": 1,
                "q3": 2,
                "q4": 1,
                "q5": 0,
                "q6": 1,
                "q7": 0,
                "q8": 1,
                "q9": 2,
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["questionnaire_code"] == "PHQ-9"
    assert payload["total_score"] == 8
    assert payload["has_safety_signal"] is True

    stored_assignment = await db_session.get(QuestionnaireAssignment, assignment.id)
    assert stored_assignment is not None
    assert stored_assignment.status == QuestionnaireAssignmentStatus.completed.value
    assert stored_assignment.completed_at is not None

    query = await db_session.execute(
        select(QuestionnaireResponse).where(QuestionnaireResponse.assignment_id == assignment.id)
    )
    stored_response = query.scalar_one_or_none()
    assert stored_response is not None
    assert stored_response.answers["q9"] == 2


async def test_patient_cannot_submit_invalid_questionnaire_answers(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_headers: dict[str, str],
    patient_user: User,
) -> None:
    assignment = await _create_assignment(
        db_session,
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        questionnaire_code=QuestionnaireCode.gad7.value,
    )

    response = await client.post(
        f"/api/v1/questionnaires/{assignment.id}/submit",
        headers=patient_headers,
        json={"answers": {"q1": 0, "q2": 0}},
    )

    assert response.status_code == 422
    assert "answers must include exactly" in response.json()["detail"]


async def test_patient_cannot_submit_completed_assignment_twice(
    client: AsyncClient,
    db_session: AsyncSession,
    doctor_user: User,
    patient_headers: dict[str, str],
    patient_user: User,
) -> None:
    submitted_at = datetime.now(UTC)
    assignment = QuestionnaireAssignment(
        patient_user_id=patient_user.id,
        doctor_user_id=doctor_user.id,
        questionnaire_code=QuestionnaireCode.phq9.value,
        status=QuestionnaireAssignmentStatus.completed.value,
        completed_at=submitted_at,
    )
    db_session.add(assignment)
    await db_session.flush()
    db_session.add(
        QuestionnaireResponse(
            assignment_id=assignment.id,
            patient_user_id=patient_user.id,
            questionnaire_code=QuestionnaireCode.phq9.value,
            answers={f"q{i}": 0 for i in range(1, 10)},
            total_score=0,
            has_safety_signal=False,
            submitted_at=submitted_at,
        )
    )
    await db_session.commit()

    response = await client.post(
        f"/api/v1/questionnaires/{assignment.id}/submit",
        headers=patient_headers,
        json={"answers": {f"q{i}": 0 for i in range(1, 10)}},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Questionnaire has already been submitted"
