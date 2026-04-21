{
  "_meta": {
    "version": "v1.6",
    "format": "SDD CONTEXT.md — Single Source of Truth for AI agent",
    "update_rule": "Bump version on schema/API/type changes. Use /context-update skill after each phase.",
    "version_scheme": "patch (v1.0→v1.1) = additive only; minor (v1.1→v1.2) = breaking change"
  },

  "captured_at": "2026-04-21",
  "phase_completed": "05",
  "phase_in_progress": null,

  "stack": {
    "db_engine": "PostgreSQL 18 alpine",
    "orm": "SQLAlchemy 2.0 async",
    "backend": "FastAPI / Pydantic v2 / Python 3.13+",
    "frontend": "Nuxt 4 / Vue 3.5+ / TypeScript / Pinia / pnpm",
    "cache": "Redis 8",
    "auth": "JWT (HS256), bcrypt",
    "infra": "Docker Compose, Alembic migrations, uv package manager"
  },

  "core_models": [
    "User (id UUID PK, email UNIQUE, hashed_password, role ENUM[admin/doctor/patient], is_active, created_at, updated_at)",
    "DoctorProfile (user_id UUID PK/FK -> users.id, created_at, updated_at)",
    "PatientProfile (user_id UUID PK/FK -> users.id, doctor_user_id UUID FK -> users.id, onboarding_status ENUM[pending/completed], must_change_password, is_active_with_doctor, created_at, updated_at)",
    "Medication (id UUID PK, patient_user_id UUID FK -> users.id, doctor_user_id UUID FK -> users.id, name, dosage_instructions, is_active, created_at, updated_at)",
    "AdherenceLog (id UUID PK, medication_id UUID FK -> medications.id, patient_user_id UUID FK -> users.id, status, deviation_note NULL, logged_at, created_at)",
    "QuestionnaireAssignment (id UUID PK, patient_user_id UUID FK -> users.id, doctor_user_id UUID FK -> users.id, questionnaire_code ENUM[PHQ-9/GAD-7], status ENUM[assigned/completed], assigned_at, completed_at NULL, created_at, updated_at)",
    "QuestionnaireResponse (id UUID PK, assignment_id UUID FK -> questionnaire_assignments.id, patient_user_id UUID FK -> users.id, questionnaire_code ENUM[PHQ-9/GAD-7], answers JSONB, total_score, has_safety_signal, submitted_at, created_at)",
    "SideEffectReport (id UUID PK, patient_user_id UUID FK -> users.id, doctor_user_id UUID FK -> users.id, medication_id UUID NULL FK -> medications.id, severity ENUM[mild/moderate/severe], symptom, note NULL, reported_at, created_at)"
  ],

  "endpoints_active": [
    "GET  /api/v1/health",
    "POST /api/v1/auth/login  — email+password → JWT access_token",
    "GET  /api/v1/auth/me     — current user (JWT required)",
    "POST /api/v1/auth/logout — stateless stub (JWT required)",
    "GET  /api/v1/patients                  — doctor roster for assigned patients (JWT doctor)",
    "POST /api/v1/patients                  — create patient account with one-time temporary password (JWT doctor)",
    "POST /api/v1/patients/{patient_id}/activate — reactivate assigned patient (JWT doctor)",
    "POST /api/v1/patients/setup-account    — patient sets permanent password and completes onboarding (JWT patient)",
    "GET  /api/v1/patients/{patient_id}/medications — assigned doctor lists a patient's active medications (JWT doctor)",
    "POST /api/v1/patients/{patient_id}/medications — assigned doctor creates a medication record for a patient (JWT doctor)",
    "GET  /api/v1/medications/current       — patient lists their current active medications (JWT patient)",
    "POST /api/v1/medications/{medication_id}/adherence — patient logs adherence for an active medication (JWT patient)",
    "GET  /api/v1/patients/{patient_id}/adherence — assigned doctor reviews patient adherence history (JWT doctor)",
    "GET  /api/v1/patients/{patient_id}/questionnaires — assigned doctor lists questionnaire assignments for an assigned patient (JWT doctor)",
    "POST /api/v1/patients/{patient_id}/questionnaires — assigned doctor assigns PHQ-9 or GAD-7 to an assigned patient (JWT doctor)",
    "GET  /api/v1/questionnaires/pending — patient lists their pending questionnaire assignments (JWT patient)",
    "POST /api/v1/questionnaires/{assignment_id}/submit — patient submits completed PHQ-9 or GAD-7 answers for scoring (JWT patient)",
    "POST /api/v1/side-effects — patient submits a side effect report for their assigned doctor with optional medication context (JWT patient)",
    "GET  /api/v1/patients/{patient_id}/side-effects — assigned doctor reviews reported side effects for a patient (JWT doctor)",
    "GET  /api/v1/patients/{patient_id}/summary — assigned doctor views aggregated questionnaire, adherence, side-effect, and safety-flag history (JWT doctor)"
  ],

  "db_schema": {
    "tables": ["users", "doctor_profiles", "patient_profiles", "medications", "adherence_logs", "questionnaire_assignments", "questionnaire_responses", "side_effect_reports"],
    "source": "alembic_versions",
    "current_head": "0005_side_effect_reports_and_patient_summary"
  },

  "ui_pages_active": [
    "/login     — auth form (blank layout)",
    "/dashboard — authenticated landing page with role-aware navigation",
    "/patients  — doctor roster and patient onboarding workspace",
    "/setup-account — patient first-login password setup flow",
    "/questionnaires/:assignmentId — patient questionnaire completion route for PHQ-9 and GAD-7 submissions"
  ],

  "env_config": {
    "keys": [
      "DATABASE_URL", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
      "REDIS_URL", "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
      "CORS_ORIGINS", "APP_ENV", "LOG_LEVEL", "API_BASE_URL"
    ]
  },

  "db_seeds": {
    "default_admin": "admin@example.com / changeme123 (migration 0001)"
  },

  "notes": "Phase 05 contract is now active: patients can report side effects, and assigned doctors can review patient summary aggregates that combine questionnaire outcomes, adherence history, and side-effect signals with explicit safety highlighting. Phase 04 questionnaire workflows, Phase 03 medication/adherence workflows, Phase 02 onboarding workflows, and Phase 01 authentication/foundation behavior remain active."
}
