# PHASE 03 — Medication tracking and adherence logging

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. Be concise. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `03` |
| Title | Medication tracking and adherence logging |
| Status | `⏳ pending` |
| Tag | `v0.3.0` |
| Depends on | PHASE_02 gate passing |
| CONTEXT.md version | `v1.3` |

---

## Phase Goal

This phase implements the next MVP outcome from `docs/SPEC.md`: a doctor assigns current medication, a patient logs whether medication was taken, and the doctor can review recent adherence history as structured records instead of relying on recall. It should extend the Phase 02 doctor-patient relationship with medication and adherence data while keeping access boundaries strict: doctors manage only their assigned patients, and patients can log adherence only for their own current medications.

---

## Scope

### Backend
- [ ] Add medication and adherence models so a doctor can record the prescribed medication and dosage context for a patient
- [ ] Implement doctor-only APIs to create and view a patient's current medication list
- [ ] Implement patient-only adherence logging APIs so a patient can record whether medication was taken and optionally record deviations
- [ ] Add backend authorization and validation so adherence history remains visible to the assigned doctor as time-based records

### Frontend
- [ ] Add a doctor workflow to record and review a patient's current medications from the existing authenticated app
- [ ] Add a patient workflow to view current medications and submit adherence logs with optional deviation notes
- [ ] Show recent adherence history in the doctor workflow so later phases can build on the same patient record

---

## Files

### Create / modify
~~~
alembic/versions/0003_medications_and_adherence.py
app/api/v1/medications.py
app/db/base.py
app/db/models/adherence_log.py
app/db/models/medication.py
app/main.py
app/schemas/medications.py
frontend/app/features/adherence/model/adherence-store.ts
frontend/app/features/adherence/ui/adherence-log-form.vue
frontend/app/features/medications/model/medication-store.ts
frontend/app/features/medications/ui/doctor-medication-form.vue
frontend/app/features/medications/ui/patient-medication-list.vue
frontend/app/pages/dashboard.vue
frontend/app/pages/patients.vue
frontend/app/shared/types/schema.ts
tests/conftest.py
tests/test_medications_api.py
frontend/tests/adherence-store.test.ts
frontend/tests/e2e/medication-adherence.spec.ts
~~~

### Do NOT touch
- `docs/SPEC.md`
- `docs/CONTEXT.md`
- `docs/SPEC_POST_MVP.md`
- Questionnaire, side-effect, doctor-summary, and safety-highlighting features planned for later phases

---

## Contracts

> This section is the source of truth for `/context-update`. Fill it in **before** handing to AI.

### New DB tables / columns
~~~
medications(
  id UUID PK,
  patient_user_id UUID NOT NULL REFERENCES users(id),
  doctor_user_id UUID NOT NULL REFERENCES users(id),
  name TEXT NOT NULL,
  dosage_instructions TEXT NOT NULL,
  is_active BOOLEAN NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)

adherence_logs(
  id UUID PK,
  medication_id UUID NOT NULL REFERENCES medications(id),
  patient_user_id UUID NOT NULL REFERENCES users(id),
  status TEXT NOT NULL,
  deviation_note TEXT NULL,
  logged_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL
)
~~~

### New API endpoints
| Method | Path | Auth | Response |
|--------|------|------|----------|
| `GET` | `/api/v1/patients/{patient_id}/medications` | JWT doctor | `{"items":[{"id":"uuid","name":"Sertraline","dosage_instructions":"50 mg once daily","is_active":true}]}` |
| `POST` | `/api/v1/patients/{patient_id}/medications` | JWT doctor | `{"id":"uuid","patient_user_id":"uuid","doctor_user_id":"uuid","name":"Sertraline","dosage_instructions":"50 mg once daily","is_active":true}` |
| `GET` | `/api/v1/medications/current` | JWT patient | `{"items":[{"id":"uuid","name":"Sertraline","dosage_instructions":"50 mg once daily","is_active":true}]}` |
| `POST` | `/api/v1/medications/{medication_id}/adherence` | JWT patient | `{"id":"uuid","medication_id":"uuid","status":"taken|missed|modified","deviation_note":"optional","logged_at":"ISO-8601"}` |
| `GET` | `/api/v1/patients/{patient_id}/adherence` | JWT doctor | `{"items":[{"id":"uuid","medication_id":"uuid","status":"taken|missed|modified","deviation_note":"optional","logged_at":"ISO-8601"}]}` |

### New TypeScript types / Pinia stores
```typescript
type MedicationItem = {
  id: string
  name: string
  dosage_instructions: string
  is_active: boolean
}

type AdherenceLogItem = {
  id: string
  medication_id: string
  status: 'taken' | 'missed' | 'modified'
  deviation_note: string | null
  logged_at: string
}

// useMedicationStore — loads doctor and patient medication lists, creates doctor-managed
// medication records, and refreshes medication data after mutations
//
// useAdherenceStore — submits patient adherence logs and loads doctor-visible adherence
// history as time-based records
```

### New env vars (add to `.env.example`)
None

---

## Gate Checks

Run `/phase-gate 03` before committing.

`/phase-gate` returns full PASS only when:
- Automated checks are green
- All architect review items below are resolved (checked off)

Use the standard infrastructure, migration, test, prep, typecheck, unit, and e2e commands from [docs/STACK.md](./STACK.md#gate-commands).

Phase-specific smoke override:

```bash
python3 - <<'PY'
import json,time,urllib.request
def post(url,payload,token=None):
    headers={"Content-Type":"application/json"}
    if token:
        headers["Authorization"]=f"Bearer {token}"
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=headers,method="POST")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())
doctor=post("http://localhost:8000/api/v1/auth/login",{"email":"doctor@example.com","password":"changeme123"})
patient=post("http://localhost:8000/api/v1/patients",{"email":f"phase03-smoke-{int(time.time())}@example.com"},doctor["access_token"])
post(f"http://localhost:8000/api/v1/patients/{patient['id']}/medications",{"name":"Phase 03 Smoke Medication","dosage_instructions":"10 mg once daily","is_active":True},doctor["access_token"])
patient_login=post("http://localhost:8000/api/v1/auth/login",{"email":patient["email"],"password":patient["temporary_password"]})
req=urllib.request.Request("http://localhost:8000/api/v1/medications/current",headers={"Authorization":f"Bearer {patient_login['access_token']}"})
with urllib.request.urlopen(req) as response:
    print(response.read().decode(), end="")
PY
# expected: Phase 03 Smoke Medication

./scripts/phase-gate.sh 03
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
feat(phase-03): add medication tracking and adherence logging
```

---

## Post-Phase Checklist

- [ ] All automated gate checks green
- [ ] All architect review notes resolved
- [ ] `docs/CONTEXT.md` updated — run `/context-update 03`
- [ ] `docs/STATE.md` phase row updated to `✅ done`
- [ ] `docs/CHANGELOG.md` entry added (if CONTEXT.md version bumped)
- [ ] Committed atomically on `feat/phase-03` branch
- [ ] Tag created after merge to develop: `git tag -a v0.3.0 -m "Phase 03: Medication tracking and adherence logging"`
