{
  "_meta": {
    "version": "v1.3",
    "format": "SDD CONTEXT.md — Single Source of Truth for AI agent",
    "update_rule": "Bump version on schema/API/type changes. Use /context-update skill after each phase.",
    "version_scheme": "patch (v1.0→v1.1) = additive only; minor (v1.1→v1.2) = breaking change"
  },

  "captured_at": "2026-04-21",
  "phase_completed": "02",
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
    "PatientProfile (user_id UUID PK/FK -> users.id, doctor_user_id UUID FK -> users.id, onboarding_status ENUM[pending/completed], must_change_password, is_active_with_doctor, created_at, updated_at)"
  ],

  "endpoints_active": [
    "GET  /api/v1/health",
    "POST /api/v1/auth/login  — email+password → JWT access_token",
    "GET  /api/v1/auth/me     — current user (JWT required)",
    "POST /api/v1/auth/logout — stateless stub (JWT required)",
    "GET  /api/v1/patients                  — doctor roster for assigned patients (JWT doctor)",
    "POST /api/v1/patients                  — create patient account with one-time temporary password (JWT doctor)",
    "POST /api/v1/patients/{patient_id}/activate — reactivate assigned patient (JWT doctor)",
    "POST /api/v1/patients/setup-account    — patient sets permanent password and completes onboarding (JWT patient)"
  ],

  "db_schema": {
    "tables": ["users", "doctor_profiles", "patient_profiles"],
    "source": "alembic_versions",
    "current_head": "0002_doctor_patient_profiles"
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

  "notes": "Phase 02 contract is now active: doctors can manage an assigned patient roster, create patient accounts with temporary passwords, reactivate linked patients, and force first-login password setup before onboarding completes. Phase 01 foundation remains active, and /phase-gate now supports phase-specific smoke overrides while re-warming the frontend after nuxt prepare for deterministic Chromium coverage."
}
