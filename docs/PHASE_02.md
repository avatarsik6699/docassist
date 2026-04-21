# PHASE 02 — Doctor-patient relationship and patient account onboarding

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. Be concise. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `02` |
| Title | Doctor-patient relationship and patient account onboarding |
| Status | `⏳ pending` |
| Tag | `v0.2.0` |
| Depends on | PHASE_01 gate passing |
| CONTEXT.md version | `v1.2` |

---

## Phase Goal

This phase implements the next MVP outcome from `docs/SPEC.md`: a doctor can create or activate a patient account and the product can enforce the rule that a patient account is linked to exactly one doctor in MVP. It should turn the Phase 01 auth foundation into a usable doctor-managed patient roster and onboarding flow so later phases can safely attach medications, questionnaires, adherence history, and side effects to the right doctor-patient relationship.

---

## Scope

### Backend
- [ ] Add the doctor-patient relationship model required by MVP, with each patient linked to exactly one doctor
- [ ] Implement doctor-only patient roster APIs for listing assigned patients and creating or activating a patient account
- [ ] Add backend validation and authorization rules so doctors can manage only their own patients and patients can access only their own records
- [ ] Implement MVP onboarding as a doctor-created patient account with a backend-generated temporary password, normal JWT login, and a required first-login password change before onboarding is marked complete

### Frontend
- [ ] Add a doctor-facing patient roster view to the authenticated app shell
- [ ] Build the doctor flow to create or activate a patient account from the web UI
- [ ] Add the patient first-access flow that redirects temporary-password sessions to `/setup-account` until the patient sets a permanent password

---

## Files

### Create / modify
~~~
.env.example
alembic/versions/0002_doctor_patient_profiles.py
app/api/v1/patients.py
app/core/auth.py
app/db/base.py
app/db/models/doctor_profile.py
app/db/models/patient_profile.py
app/db/models/user.py
app/main.py
app/schemas/profiles.py
app/schemas/users.py
frontend/app/features/auth/model/auth-store.ts
frontend/app/features/patient-roster/model/patient-roster-store.ts
frontend/app/features/patient-roster/ui/patient-roster-table.vue
frontend/app/features/patient-roster/ui/patient-onboarding-form.vue
frontend/app/pages/dashboard.vue
frontend/app/pages/patients.vue
frontend/app/pages/setup-account.vue
frontend/app/shared/types/schema.ts
tests/conftest.py
tests/test_patients_api.py
frontend/tests/patient-roster-store.test.ts
frontend/tests/e2e/patient-onboarding.spec.ts
~~~

### Do NOT touch
- `docs/SPEC.md`
- `docs/CONTEXT.md`
- `docs/SPEC_POST_MVP.md`
- Medication, adherence, questionnaire, side-effect, and doctor-summary features planned for later phases

---

## Contracts

> This section is the source of truth for `/context-update`. Fill it in **before** handing to AI.

### New DB tables / columns
~~~
doctor_profiles(
  user_id UUID PK REFERENCES users(id),
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)

patient_profiles(
  user_id UUID PK REFERENCES users(id),
  doctor_user_id UUID NOT NULL REFERENCES users(id),
  onboarding_status TEXT NOT NULL,
  must_change_password BOOLEAN NOT NULL,
  is_active_with_doctor BOOLEAN NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
~~~

### New API endpoints
| Method | Path | Auth | Response |
|--------|------|------|----------|
| `GET` | `/api/v1/patients` | JWT doctor | `{"items":[{"id":"uuid","email":"patient@example.com","is_active":true,"onboarding_status":"pending|completed"}]}` |
| `POST` | `/api/v1/patients` | JWT doctor | `{"id":"uuid","email":"patient@example.com","doctor_user_id":"uuid","onboarding_status":"pending","temporary_password":"generated-once"}` |
| `POST` | `/api/v1/patients/{patient_id}/activate` | JWT doctor | `{"id":"uuid","is_active":true,"onboarding_status":"pending|completed"}` |
| `POST` | `/api/v1/patients/setup-account` | JWT patient | `{"id":"uuid","email":"patient@example.com","onboarding_status":"completed","must_change_password":false}` |

### New TypeScript types / Pinia stores
```typescript
type PatientRosterItem = {
  id: string
  email: string
  is_active: boolean
  onboarding_status: 'pending' | 'completed'
}

type CreatePatientResult = {
  id: string
  email: string
  doctor_user_id: string
  onboarding_status: 'pending'
  temporary_password: string
}

// usePatientRosterStore — loads the current doctor's patients, creates or activates
// patient accounts, and drives roster refresh in the doctor UI
```

### New env vars (add to `.env.example`)
<!-- Replace with a table when this phase introduces any. -->
None

---

## Gate Checks

Run `/phase-gate 02` before committing.

`/phase-gate` returns full PASS only when:
- Automated checks are green
- All architect review items below are resolved (checked off)

Use the standard infrastructure, migration, test, prep, typecheck, unit, and e2e commands from [docs/STACK.md](./STACK.md#gate-commands).

Phase-specific smoke override:

```bash
curl -s http://localhost:8000/api/v1/patients
# expected: doctor-authenticated patient roster response

./scripts/phase-gate.sh 02
```

---

## Architect Review Notes

Use this section after manual verification. Add one checkbox item per issue the architect wants fixed before the phase can close.
Leave the item unchecked while it is still open. Check it off only after the fix is implemented and re-verified.
If manual verification found nothing, keep the default checked line below.

- [x] No architect review issues recorded

---

## Atomic Commit Message

```text
feat(phase-02): add doctor patient relationship and onboarding flow
```

---

## Post-Phase Checklist

- [ ] All automated gate checks green
- [ ] All architect review notes resolved
- [ ] `docs/CONTEXT.md` updated — run `/context-update 02`
- [ ] `docs/STATE.md` phase row updated to `✅ done`
- [ ] `docs/CHANGELOG.md` entry added (if CONTEXT.md version bumped)
- [ ] Committed atomically on `feat/phase-02` branch
- [ ] Tag created after merge to develop: `git tag -a v0.2.0 -m "Phase 02: Doctor-patient relationship and patient account onboarding"`
