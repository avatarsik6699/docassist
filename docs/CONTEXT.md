{
  "_meta": {
    "version": "v1.4",
    "format": "SDD CONTEXT.md — Single Source of Truth for AI agent",
    "update_rule": "Bump version on schema/API/type changes. Use /context-update skill after each phase.",
    "version_scheme": "patch (v1.0→v1.1) = additive only; minor (v1.1→v1.2) = breaking change"
  },

  "captured_at": "2026-04-21",
  "phase_completed": "03",
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
    "AdherenceLog (id UUID PK, medication_id UUID FK -> medications.id, patient_user_id UUID FK -> users.id, status, deviation_note NULL, logged_at, created_at)"
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
    "GET  /api/v1/patients/{patient_id}/adherence — assigned doctor reviews patient adherence history (JWT doctor)"
  ],

  "db_schema": {
    "tables": ["users", "doctor_profiles", "patient_profiles", "medications", "adherence_logs"],
    "source": "alembic_versions",
    "current_head": "0003_medications_and_adherence"
  },

  "ui_pages_active": [
    "/login     — auth form (blank layout)",
    "/dashboard — authenticated landing page with role-aware navigation",
    "/patients  — doctor roster and patient onboarding workspace",
    "/setup-account — patient first-login password setup flow"
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

  "notes": "Phase 03 contract is now active: assigned doctors can create and review active medications for linked patients, patients can view their current medications and log adherence outcomes, and doctors can review those adherence records as structured history. Phase 02 doctor-patient onboarding remains active, and Phase 01 authentication/foundation behavior remains unchanged."
}
