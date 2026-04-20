# TECHNICAL SPECIFICATION (SPEC.md): `Docassist`

> **For AI agent**: Read this file in full before starting any phase.
> Confirm understanding of constraints and the phased development model.
> When this file changes, run `/spec-sync [description of change]` immediately.

## Metadata

| Field | Value |
|-------|-------|
| Document Version | `v1.0` |
| Date | `2026-04-19` |
| Architect / Owner | `v.godlevskiy` |
| Contract Version | `v1.0` (see `docs/CONTEXT.md`) |
| Stack | Nuxt 4 (Vue 3.5+, TS, pnpm), FastAPI latest, SQLAlchemy 2.0 (async), PostgreSQL 18, Redis 8, Docker Compose |
| AI Agent | Claude Code (Agent Mode) |
| Domain | CDSS + RPM — Continuous patient monitoring between clinical appointments; initial focus: psychiatry |

---

## 1. Project Overview and Goals

### 1.1 Problem

Between psychiatric appointments (typically 4–6 weeks apart) there is a complete data void: the doctor has no objective picture of how the patient is feeling, whether the medication is working, whether there are side effects, or whether the patient is actually taking the prescribed doses. All decisions at the next appointment are based on patient recall and the doctor's memory — not on real dynamics. This creates:

- **Loss of dynamics**: improvements and deteriorations happen between visits and go unrecorded
- **Reliance on memory**: both patient and doctor reconstruct history subjectively
- **Low adherence**: no structured mechanism to track whether the patient takes medication as prescribed
- **Missing structured data**: no time-series data on symptom severity, making it impossible to evaluate therapy effect objectively
- **Delayed response to emergencies**: severe side effects or clinical deterioration may not be reported until the next appointment

### 1.2 Goal and Success Metrics

**Goal**: Provide a continuous monitoring loop between clinical appointments, translating subjective patient experience into objective, structured, time-series data — so the doctor opens the patient's profile and immediately sees the current picture, not a memory.

| Metric | Target |
|--------|--------|
| Doctor can see patient's full dynamics in < 30 seconds | ✅ on dashboard open |
| System detects clinically significant improvement/deterioration | ✅ automated per validated scale thresholds |
| Patient adherence captured at dose level | ✅ daily log |
| Alert delivered to doctor on critical events | ✅ within 24 hours of trigger |
| Questionnaire completion rate (engagement) | ≥ 70% scheduled submissions |
| Time to identify comorbidity dynamics pattern | < 5 minutes on analytics page |

### 1.3 Project Boundaries

| Included | Excluded |
|----------|----------|
| Continuous monitoring between appointments | Direct teleconsultation / video visits |
| Validated psychiatric questionnaires (PHQ-9, GAD-7 and others) | AI/LLM clinical recommendations |
| Medication & dose tracking | E-prescribing / pharmacy integration |
| Adherence logging (actual dose taken) | EMR/EHR system integration (v1) |
| Side effect reporting by patient | Billing / insurance |
| Clinical significance detection (rule-based) | Diagnosis suggestion |
| Comorbidity dynamics comparison | Multi-clinic shared records (v1) |
| Alerts & reminders (doctor + patient) | SMS / push (email only in v1) |
| Doctor dashboard with charts | Patient-to-patient communication |
| Admin panel (users, medications, scales) | Mobile native app (v1 is web-only) |
| Multi-specialty architecture (data model is specialty-agnostic) | Non-psychiatric specialties in v1 (data model supports, UI does not yet) |

---

## 2. Domain Context

### 2.1 Roles and Permissions

| Role | Capabilities | Restrictions |
|------|-------------|--------------|
| `admin` | Manage all users; manage medication catalog; manage questionnaire templates; view system stats | Cannot see patient clinical data |
| `doctor` | Register patients; assign questionnaires; prescribe medications; view patient dynamics; acknowledge alerts; add therapy reviews | Can only see own assigned patients |
| `patient` | Fill in assigned questionnaires; log medication adherence; report side effects; view own history | Cannot see other patients; cannot see doctor notes (v1) |
| `AI_Agent` | Implements phases, runs gate checks | No push to main/develop; no hardcoded secrets |

### 2.2 Key Entities and Relationships

```
User ──── DoctorProfile ────< PatientProfile >──── User
                                    │
                    ┌───────────────┼────────────────────┐
                    │               │                    │
          PatientMedication  QuestionnaireAssignment  SideEffectReport
                    │               │
           AdherenceLog    QuestionnaireResponse
                                    │
                              ClinicalAlert
```

### 2.3 Clinical Domain Rules

1. **Clinical significance** is defined per questionnaire using validated thresholds (not custom):
   - **PHQ-9** (depression, 0–27): Response = ≥50% score reduction from baseline; Remission = score < 5
   - **GAD-7** (anxiety, 0–21): Response = ≥50% score reduction; Remission = score < 5
   - Additional scales use same pattern — thresholds stored in `questionnaire_templates.scoring_rules` (JSONB)

2. **Therapy evaluation window**: Each medication dose has a minimum evaluation window (default: 4 weeks for antidepressants). The system flags "review due" after this window with no assessment.

3. **Comorbidity hypothesis**: When two questionnaires are both assigned, the system computes temporal lag of improvement — the scale that improves first is surfaced as potentially primary. This is presented as a data observation, not a diagnosis.

4. **Alert severity levels**:
   - `info` — reminder (questionnaire due, evaluation window approaching)
   - `warning` — no response after evaluation window, mild deterioration
   - `critical` — severe side effect (severity ≥ 4), score worsening ≥ 30%, suicidal ideation flag (PHQ-9 Q9)

5. **Specialty-agnostic design**: `questionnaire_templates`, `medications`, and `side_effect_reports` are not hardcoded to psychiatry. The `specialty` field allows future specialties to coexist.

---

## 3. Data Model (SQLAlchemy 2.0 Async)

```text
users(
  id              UUID         PK DEFAULT gen_random_uuid(),
  email           VARCHAR      UNIQUE NOT NULL,
  hashed_password VARCHAR      NOT NULL,
  role            userrole     NOT NULL,          -- enum: admin, doctor, patient
  full_name       VARCHAR      NOT NULL,
  is_active       BOOLEAN      NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

doctor_profiles(
  id              UUID         PK DEFAULT gen_random_uuid(),
  user_id         UUID         FK users UNIQUE NOT NULL,
  specialty       VARCHAR      NOT NULL DEFAULT 'psychiatry',
  license_number  VARCHAR,
  clinic_name     VARCHAR,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

patient_profiles(
  id              UUID         PK DEFAULT gen_random_uuid(),
  user_id         UUID         FK users UNIQUE NOT NULL,
  doctor_id       UUID         FK doctor_profiles NOT NULL,
  birth_date      DATE         NOT NULL,
  gender          VARCHAR      NOT NULL,          -- male, female, other
  diagnosis_notes TEXT,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

medications(
  id              UUID         PK DEFAULT gen_random_uuid(),
  name            VARCHAR      NOT NULL,          -- brand name
  generic_name    VARCHAR      NOT NULL,
  drug_class      VARCHAR      NOT NULL,          -- antidepressant, anxiolytic, antipsychotic, mood_stabilizer, other
  typical_dose_min NUMERIC,
  typical_dose_max NUMERIC,
  dose_unit       VARCHAR      NOT NULL DEFAULT 'mg',
  is_active       BOOLEAN      NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

patient_medications(
  id              UUID         PK DEFAULT gen_random_uuid(),
  patient_id      UUID         FK patient_profiles NOT NULL,
  medication_id   UUID         FK medications NOT NULL,
  dose            NUMERIC      NOT NULL,
  dose_unit       VARCHAR      NOT NULL DEFAULT 'mg',
  frequency       VARCHAR      NOT NULL,          -- '1x/day', '2x/day', 'as needed'
  instructions    TEXT,
  prescribed_by   UUID         FK doctor_profiles,
  started_at      DATE         NOT NULL,
  ended_at        DATE,
  is_active       BOOLEAN      NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

adherence_logs(
  id                    UUID    PK DEFAULT gen_random_uuid(),
  patient_id            UUID    FK patient_profiles NOT NULL,
  patient_medication_id UUID    FK patient_medications NOT NULL,
  log_date              DATE    NOT NULL,
  taken                 BOOLEAN NOT NULL DEFAULT true,
  actual_dose           NUMERIC,                 -- may differ from prescribed
  reason_skipped        VARCHAR,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(patient_medication_id, log_date)
)

questionnaire_templates(
  id              UUID         PK DEFAULT gen_random_uuid(),
  code            VARCHAR      UNIQUE NOT NULL,  -- 'PHQ-9', 'GAD-7', 'MADRS', etc.
  name            VARCHAR      NOT NULL,
  specialty       VARCHAR      NOT NULL DEFAULT 'psychiatry',
  description     TEXT,
  version         VARCHAR      NOT NULL DEFAULT '1.0',
  total_min_score INT          NOT NULL DEFAULT 0,
  total_max_score INT          NOT NULL,
  scoring_rules   JSONB        NOT NULL,         -- {bands: [{min,max,label}], response_threshold_pct: 50, remission_score: 5}
  is_active       BOOLEAN      NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

questionnaire_questions(
  id              UUID         PK DEFAULT gen_random_uuid(),
  template_id     UUID         FK questionnaire_templates NOT NULL,
  question_number INT          NOT NULL,
  text            TEXT         NOT NULL,
  answer_options  JSONB        NOT NULL,         -- [{value: 0, label: "Not at all"}, ...]
  is_safety_flag  BOOLEAN      NOT NULL DEFAULT false,  -- true for suicidal ideation Q
  weight          NUMERIC      NOT NULL DEFAULT 1.0
)

questionnaire_assignments(
  id              UUID         PK DEFAULT gen_random_uuid(),
  patient_id      UUID         FK patient_profiles NOT NULL,
  template_id     UUID         FK questionnaire_templates NOT NULL,
  assigned_by     UUID         FK doctor_profiles NOT NULL,
  frequency_days  INT          NOT NULL DEFAULT 7,  -- submit every N days
  next_due_at     TIMESTAMPTZ  NOT NULL,
  is_active       BOOLEAN      NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

questionnaire_responses(
  id              UUID         PK DEFAULT gen_random_uuid(),
  patient_id      UUID         FK patient_profiles NOT NULL,
  assignment_id   UUID         FK questionnaire_assignments NOT NULL,
  template_id     UUID         FK questionnaire_templates NOT NULL,
  submitted_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
  answers         JSONB        NOT NULL,         -- {question_id: answer_value, ...}
  total_score     INT          NOT NULL,
  interpretation  VARCHAR      NOT NULL,         -- 'minimal','mild','moderate','severe'
  has_safety_flag BOOLEAN      NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
)

side_effect_reports(
  id                    UUID    PK DEFAULT gen_random_uuid(),
  patient_id            UUID    FK patient_profiles NOT NULL,
  patient_medication_id UUID    FK patient_medications,  -- nullable: unknown source
  symptom_name          VARCHAR NOT NULL,
  severity              INT     NOT NULL,                -- 1 (mild) – 5 (severe)
  onset_date            DATE    NOT NULL,
  resolved_date         DATE,
  is_resolved           BOOLEAN NOT NULL DEFAULT false,
  notes                 TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
)

clinical_alerts(
  id                UUID         PK DEFAULT gen_random_uuid(),
  patient_id        UUID         FK patient_profiles NOT NULL,
  doctor_id         UUID         FK doctor_profiles NOT NULL,
  alert_type        VARCHAR      NOT NULL,  -- deterioration | no_improvement | severe_side_effect | medication_review_due | missed_questionnaire | safety_flag
  severity          VARCHAR      NOT NULL,  -- info | warning | critical
  title             VARCHAR      NOT NULL,
  message           TEXT         NOT NULL,
  metadata          JSONB,                  -- {scale: 'PHQ-9', score: 18, baseline: 12, delta_pct: 50}
  is_acknowledged   BOOLEAN      NOT NULL DEFAULT false,
  acknowledged_at   TIMESTAMPTZ,
  created_at        TIMESTAMPTZ  NOT NULL DEFAULT now()
)

therapy_reviews(
  id          UUID         PK DEFAULT gen_random_uuid(),
  patient_id  UUID         FK patient_profiles NOT NULL,
  doctor_id   UUID         FK doctor_profiles NOT NULL,
  reviewed_at TIMESTAMPTZ  NOT NULL,
  notes       TEXT,
  decision    VARCHAR,     -- continue | adjust_dose | switch_medication | add_medication | taper | discontinue
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
)
```

---

## 4. API and Backend (FastAPI + Python)

### 4.1 Architecture

```
app/
├── api/
│   └── v1/
│       ├── health.py          (GET /health)
│       ├── auth.py            (login, me, logout)
│       ├── admin/
│       │   ├── users.py
│       │   ├── medications.py
│       │   └── questionnaires.py
│       ├── doctor/
│       │   ├── patients.py
│       │   ├── medications.py
│       │   ├── questionnaires.py
│       │   ├── alerts.py
│       │   └── reviews.py
│       ├── patient/
│       │   ├── me.py
│       │   ├── questionnaires.py
│       │   ├── adherence.py
│       │   └── side_effects.py
│       └── analytics/
│           └── dynamics.py
├── core/
│   ├── config.py              (Pydantic Settings)
│   ├── auth.py                (JWT + bcrypt + RBAC)
│   ├── alerts.py              (alert generation engine)
│   └── exceptions.py
├── db/
│   ├── base.py                (Base + UUID/Timestamp mixins)
│   ├── session.py             (async_sessionmaker + get_db)
│   ├── models/                (one file per entity)
│   └── alembic/
├── services/
│   ├── analytics.py           (dynamics, trend, clinical significance)
│   ├── alert_engine.py        (rule-based alert generation)
│   └── scoring.py             (questionnaire scoring logic)
└── schemas/                   (Pydantic v2 — one file per domain)
```

### 4.2 Core Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/v1/health` | — | Health + DB check |
| `POST` | `/api/v1/auth/login` | — | JWT login |
| `GET`  | `/api/v1/auth/me` | JWT | Current user |
| `POST` | `/api/v1/auth/logout` | JWT | Invalidate token |
| **Admin** | | | |
| `GET`  | `/api/v1/admin/users` | JWT+admin | List all users |
| `POST` | `/api/v1/admin/users` | JWT+admin | Create user |
| `PATCH`| `/api/v1/admin/users/{id}` | JWT+admin | Update user |
| `GET`  | `/api/v1/admin/medications` | JWT+admin | Medication catalog |
| `POST` | `/api/v1/admin/medications` | JWT+admin | Add medication |
| `PATCH`| `/api/v1/admin/medications/{id}` | JWT+admin | Update medication |
| `GET`  | `/api/v1/admin/questionnaire-templates` | JWT+admin | List templates |
| `POST` | `/api/v1/admin/questionnaire-templates` | JWT+admin | Add template |
| **Doctor** | | | |
| `GET`  | `/api/v1/doctor/patients` | JWT+doctor | My patient list (with alert badges) |
| `POST` | `/api/v1/doctor/patients` | JWT+doctor | Register new patient |
| `GET`  | `/api/v1/doctor/patients/{id}` | JWT+doctor | Patient full profile |
| `GET`  | `/api/v1/doctor/patients/{id}/summary` | JWT+doctor | Dashboard card summary |
| `GET`  | `/api/v1/doctor/patients/{id}/medications` | JWT+doctor | Medication timeline |
| `POST` | `/api/v1/doctor/patients/{id}/medications` | JWT+doctor | Prescribe medication |
| `PATCH`| `/api/v1/doctor/patients/{id}/medications/{med_id}` | JWT+doctor | Update/discontinue |
| `GET`  | `/api/v1/doctor/patients/{id}/questionnaire-responses` | JWT+doctor | All responses |
| `POST` | `/api/v1/doctor/patients/{id}/questionnaire-assignments` | JWT+doctor | Assign questionnaire |
| `GET`  | `/api/v1/doctor/patients/{id}/analytics` | JWT+doctor | Dynamics, trends, significance |
| `GET`  | `/api/v1/doctor/patients/{id}/side-effects` | JWT+doctor | All reported side effects |
| `GET`  | `/api/v1/doctor/patients/{id}/alerts` | JWT+doctor | Patient alerts |
| `POST` | `/api/v1/doctor/patients/{id}/alerts/{alert_id}/acknowledge` | JWT+doctor | Acknowledge alert |
| `GET`  | `/api/v1/doctor/alerts` | JWT+doctor | All active alerts across my patients |
| `POST` | `/api/v1/doctor/patients/{id}/therapy-reviews` | JWT+doctor | Add therapy review |
| **Patient** | | | |
| `GET`  | `/api/v1/patient/me` | JWT+patient | Own profile |
| `GET`  | `/api/v1/patient/medications` | JWT+patient | Current medications |
| `POST` | `/api/v1/patient/adherence` | JWT+patient | Log daily adherence |
| `GET`  | `/api/v1/patient/questionnaires/pending` | JWT+patient | Pending questionnaires |
| `POST` | `/api/v1/patient/questionnaires/{assignment_id}/respond` | JWT+patient | Submit response |
| `GET`  | `/api/v1/patient/questionnaires/history` | JWT+patient | Past responses |
| `POST` | `/api/v1/patient/side-effects` | JWT+patient | Report side effect |
| `GET`  | `/api/v1/patient/side-effects` | JWT+patient | Own side effects |
| `PATCH`| `/api/v1/patient/side-effects/{id}` | JWT+patient | Update (mark resolved) |
| **Analytics** | | | |
| `GET`  | `/api/v1/analytics/patients/{id}/dynamics` | JWT+doctor | Time-series per scale |
| `GET`  | `/api/v1/analytics/patients/{id}/comorbidity` | JWT+doctor | Cross-scale comparison |
| `GET`  | `/api/v1/analytics/patients/{id}/therapy-effect` | JWT+doctor | Drug response evaluation |

### 4.3 Code Requirements

- 100% type hints, Pydantic v2, async/await throughout
- Dependencies via `uv` (`pyproject.toml` + `uv.lock`); do not use `pip-tools`
- RBAC via FastAPI `Depends` + JWT scopes (role encoded in token)
- No hardcoded secrets — use `.env` / Pydantic Settings only
- Doctor can only access data for their own assigned patients (enforced in service layer, not just router)
- All patient clinical data access is logged (audit trail via middleware)

---

## 5. Frontend (Nuxt 4 + Vue 3.5+ + TypeScript)

### 5.1 Pages

```
pages/
├── login.vue                        (public, blank layout)
├── dashboard.vue                    (doctor: patient list + global alerts)
├── patients/
│   ├── [id]/index.vue               (patient overview: summary card)
│   ├── [id]/medications.vue         (medication timeline + prescribe)
│   ├── [id]/questionnaires.vue      (assignments + response history)
│   ├── [id]/analytics.vue           (dynamics charts + comorbidity)
│   ├── [id]/side-effects.vue        (side effect list)
│   └── [id]/alerts.vue              (alert history)
├── my-health/
│   ├── index.vue                    (patient: own dashboard)
│   ├── medications.vue              (own medications + adherence log)
│   ├── questionnaire/[id].vue       (fill in questionnaire)
│   └── side-effects.vue            (report + list own side effects)
└── admin/
    ├── users.vue
    ├── medications.vue
    └── questionnaires.vue
```

### 5.2 Components and Stores

```
components/
├── ui/                             (Button, Modal, Toast, Badge, Spinner, Alert)
├── charts/
│   ├── ScoreDynamicsChart.vue      (time-series line chart per scale)
│   ├── ComorbidityChart.vue        (multi-scale overlay chart)
│   └── MedicationTimeline.vue      (Gantt-like medication bar)
├── patient/
│   ├── PatientCard.vue             (dashboard list item with alert badge)
│   ├── PatientSummary.vue          (header card: meds, last score, days on dose)
│   └── AlertBanner.vue             (critical alert highlight)
├── questionnaire/
│   ├── QuestionnaireForm.vue       (renders questions from template)
│   └── ResponseHistoryRow.vue
└── medications/
    ├── PrescriptionForm.vue
    └── AdherenceToggle.vue

stores/
├── auth.ts                         (login, fetchMe, logout, token, user, isAuthenticated)
├── ui.ts                           (sidebar, loading, toast)
├── patients.ts                     (patient list, selected patient)
├── medications.ts                  (catalog, patient prescriptions, adherence)
├── questionnaires.ts               (templates, assignments, responses, pending)
├── alerts.ts                       (alerts list, acknowledge)
└── analytics.ts                    (dynamics data, comorbidity data)

composables/
├── useApi.ts                       (typed fetch wrapper with auth header)
├── usePatientGuard.ts              (doctor-only: verifies patient belongs to me)
└── useClinicalColor.ts             (maps severity/trend to color tokens)
```

---

## 6. Infrastructure and CI/CD

### 6.1 Docker

```
docker-compose.yml       (backend, frontend, postgres, redis, nginx)
Dockerfile.backend       (python + uv)
Dockerfile.frontend      (node + pnpm + nuxt build)
nginx/nginx.conf         (reverse proxy: /api → backend:8000, / → frontend:3000)
```

### 6.2 CI (GitHub Actions)

- `lint` — ruff (backend), tsc --noEmit (frontend)
- `test-backend` — pytest + postgres service container
- `test-frontend` — vitest
- `build` — docker images (dry-run, no push on PR)

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Security | No hardcoded secrets; bcrypt ≥ 12 rounds; JWT expiry ≤ 60 min; patient data isolated by doctor_id at service layer |
| Audit | All reads/writes to patient clinical data logged (user_id, action, resource, timestamp) |
| Privacy | No real patient names or diagnoses in logs; pseudonymized patient IDs in log lines |
| Test coverage | Backend ≥ 70%, Frontend ≥ 70% |
| Type safety | 100% type hints (Python strict), strict TypeScript |
| Performance | Health endpoint p99 < 200 ms; analytics endpoint p99 < 1 s |
| Environments | `development`, `staging`, `production` |
| Data integrity | Safety-flagged responses (PHQ-9 Q9 ≥ 1) immediately generate `critical` alert — never silently dropped |
| Specialty isolation | Each questionnaire, medication, and alert carries a `specialty` tag; the system can serve multiple specialties without data mixing |

---

## 8. Development Phases (AI-Optimized)

> **AI agent rule**: implement phases strictly in order.
> After each phase: run gate checks, commit atomically, update `STATE.md`.
> Do NOT start Phase N+1 until Phase N gate is green.
> ⚠️ When this file changes, run `/spec-sync [description]` immediately.

### Phase 1: Foundation & Core Data
- **Scope**: Docker infra (postgres, redis, backend, frontend, nginx), `users` table, Alembic, JWT auth (`/login`, `/me`, `/logout`), Nuxt skeleton with auth guard, CI pipeline
- **Gate**: `docker compose up` → all services healthy; `pytest` → pass; `tsc --noEmit` → OK; `vitest` → pass

### Phase 2: User Management & Patient-Doctor Profiles
- **Scope**: `doctor_profiles`, `patient_profiles` tables; admin user CRUD; doctor registers patient; doctor-patient assignment; patient invitation flow (account created by doctor, patient sets password via token); role-based page guards
- **Gate**: Doctor can register patient; patient can log in; doctor cannot see other doctor's patients

### Phase 3: Medications & Adherence Tracking
- **Scope**: `medications` catalog (admin-managed, seeded with common psychiatric drugs); `patient_medications` (doctor prescribes); `adherence_logs` (patient logs daily intake, actual dose); medication timeline view on doctor side; patient sees own medications
- **Gate**: Doctor prescribes → patient sees medication; patient logs adherence → doctor sees actual vs prescribed

### Phase 4: Questionnaires & Scoring Engine
- **Scope**: `questionnaire_templates`, `questionnaire_questions` (seeded: PHQ-9, GAD-7); `questionnaire_assignments` (doctor assigns with frequency); patient fills form → `questionnaire_responses` with automated scoring, band interpretation, safety flag detection; response history view
- **Gate**: PHQ-9 and GAD-7 score correctly against validated answer sets; safety flag on Q9 ≥ 1 is recorded; doctor sees response history

### Phase 5: Clinical Analytics & Dynamics
- **Scope**: `analytics.py` service — time-series aggregation of scores per scale; trend detection (improving/stable/deteriorating over last 3 points); clinical significance calculation (response = baseline ×50% reduction, remission threshold); therapy duration counter per medication/dose; `analytics/dynamics` and `analytics/therapy-effect` endpoints; ScoreDynamicsChart component
- **Gate**: PHQ-9 time-series returns correct scores; system correctly flags response and remission; medication days-on-dose counter is accurate

### Phase 6: Alert Engine
- **Scope**: `clinical_alerts` table; `alert_engine.py` — rule-based alert generation triggered after each questionnaire response and adherence log; alert types: `deterioration` (≥30% score worsening), `no_improvement` (no response after evaluation window), `severe_side_effect` (severity ≥ 4), `medication_review_due` (window elapsed, no review), `missed_questionnaire` (overdue > 48 h), `safety_flag` (PHQ-9 Q9); doctor global alert list; per-patient alert list; acknowledge endpoint; AlertBanner component
- **Gate**: Inserting a deteriorating response triggers alert; safety flag triggers critical alert immediately; doctor acknowledges → alert disappears from active list

### Phase 7: Doctor Dashboard & Patient Overview
- **Scope**: Doctor dashboard (`/dashboard`) — patient list with unacknowledged alert count badges, sorted by severity; patient detail page — PatientSummary card (current medications, doses, days on dose, last score per scale, last adherence); charts: ScoreDynamicsChart (multi-scale overlay), MedicationTimeline (Gantt bar); therapy review form
- **Gate**: Dashboard loads patient list in < 2 s with 50 patients seeded; all chart data is correct; patient summary card reflects latest data

### Phase 8: Comorbidity Analysis
- **Scope**: `analytics/comorbidity` endpoint — for patients with ≥ 2 assigned scales, compute temporal lag of first meaningful improvement (response) per scale; return ordered list (which improved first); ComorbidityChart component (overlaid multi-scale time-series with response threshold lines); UI panel on analytics page
- **Gate**: Patient with PHQ-9 improving before GAD-7 → system identifies PHQ-9 as first-responder; chart renders both scales with correct threshold lines

---

## 9. Glossary

| Term | Definition |
|------|------------|
| `CDSS` | Clinical Decision Support System — software that assists clinicians in making decisions |
| `RPM` | Remote Patient Monitoring — continuous data collection outside clinical settings |
| `PHQ-9` | Patient Health Questionnaire-9 — validated 9-item scale for depression severity (0–27) |
| `GAD-7` | Generalized Anxiety Disorder-7 — validated 7-item scale for anxiety severity (0–21) |
| `Response` | ≥50% reduction in baseline scale score — clinically meaningful improvement |
| `Remission` | Score falls below the scale-specific remission threshold (e.g., PHQ-9 < 5) |
| `Evaluation window` | Minimum time a patient must be on a dose before the system expects assessable effect |
| `Safety flag` | Response to a suicidal ideation question (e.g., PHQ-9 Q9) with score ≥ 1 — triggers critical alert |
| `Comorbidity` | Presence of two or more co-occurring disorders (e.g., depression + anxiety) |
| `Adherence` | Degree to which the patient takes medication as prescribed |
| `Gate` | Set of checks (tests, lint, type-check, smoke) that must all pass before committing a phase |
| `CONTEXT.md` | Living technical contract: current DB schema, active endpoints, TS types, env vars |
| `STATE.md` | Operational tracker: phase statuses, blockers, expert feedback |
| `CHANGELOG.md` | History of spec/architecture changes and their impact |
