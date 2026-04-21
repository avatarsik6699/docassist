# PHASE 05 — Doctor patient view with recent history and safety highlighting

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. Be concise. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `05` |
| Title | Doctor patient view with recent history and safety highlighting |
| Status | `⏳ pending` |
| Tag | `v0.5.0` |
| Depends on | PHASE_04 gate passing |
| CONTEXT.md version | `v1.5` |

---

## Phase Goal

This phase implements the next MVP outcome from `docs/SPEC.md`: a doctor opens the patient record and sees recent questionnaire submissions, adherence history, and side effects in one place, with urgent safety items highlighted. It should complete the MVP review loop so doctors can assess a patient's between-visit status quickly without reconstructing data from memory.

---

## Scope

### Backend
- [ ] Add side-effect reporting data model and APIs so patients can submit severity-tagged side effects with optional clinical context
- [ ] Implement doctor-only patient summary APIs that combine recent questionnaire scores, adherence history, and side-effect reports for assigned patients
- [ ] Add explicit safety highlighting logic for defined safety signals from questionnaire responses and severe side-effect reports
- [ ] Enforce existing access boundaries so doctors can access only assigned patients and patients can submit only their own side-effect reports

### Frontend
- [ ] Add a doctor patient summary workspace that presents recent questionnaire, adherence, and side-effect history in one review surface
- [ ] Add visible safety-priority markers for explicit safety rules so urgent items stand out in the doctor workflow
- [ ] Add a patient side-effect reporting flow in the authenticated app that works on desktop and mobile

---

## Files

### Create / modify
~~~
alembic/versions/0005_side_effect_reports_and_patient_summary.py
app/api/v1/patient_summary.py
app/api/v1/side_effects.py
app/db/base.py
app/db/models/side_effect_report.py
app/main.py
app/schemas/patient_summary.py
app/schemas/side_effects.py
frontend/app/features/patient-summary/model/patient-summary-store.ts
frontend/app/features/patient-summary/ui/patient-summary-panel.vue
frontend/app/features/side-effects/model/side-effects-store.ts
frontend/app/features/side-effects/ui/side-effect-report-form.vue
frontend/app/pages/patients.vue
frontend/app/shared/types/schema.ts
tests/conftest.py
tests/test_patient_summary_api.py
tests/test_side_effects_api.py
frontend/tests/e2e/patient-summary-safety.spec.ts
frontend/tests/side-effects-store.test.ts
~~~

### Do NOT touch
- `docs/SPEC.md`
- `docs/CONTEXT.md`
- `docs/SPEC_POST_MVP.md`
- Authentication foundation and onboarding contracts completed in earlier phases, except integration points needed for this phase

---

## Contracts

> This section is the source of truth for `/context-update`. Fill it in **before** handing to AI.

### New DB tables / columns
~~~
side_effect_reports(
  id UUID PK,
  patient_user_id UUID NOT NULL REFERENCES users(id),
  doctor_user_id UUID NOT NULL REFERENCES users(id),
  medication_id UUID NULL REFERENCES medications(id),
  severity TEXT NOT NULL,
  symptom TEXT NOT NULL,
  note TEXT NULL,
  reported_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL
)
~~~

### New API endpoints
| Method | Path | Auth | Response |
|--------|------|------|----------|
| `POST` | `/api/v1/side-effects` | JWT patient | `{"id":"uuid","patient_user_id":"uuid","doctor_user_id":"uuid","medication_id":"uuid|null","severity":"mild|moderate|severe","symptom":"text","note":"text|null","reported_at":"ISO-8601"}` |
| `GET` | `/api/v1/patients/{patient_id}/side-effects` | JWT doctor | `{"items":[{"id":"uuid","severity":"mild|moderate|severe","symptom":"text","note":"text|null","reported_at":"ISO-8601"}]}` |
| `GET` | `/api/v1/patients/{patient_id}/summary` | JWT doctor | `{"patient_id":"uuid","questionnaires":[{"assignment_id":"uuid","questionnaire_code":"PHQ-9|GAD-7","total_score":0,"has_safety_signal":false,"submitted_at":"ISO-8601"}],"adherence":[{"id":"uuid","medication_id":"uuid","status":"taken|missed|modified","logged_at":"ISO-8601"}],"side_effects":[{"id":"uuid","severity":"mild|moderate|severe","symptom":"text","reported_at":"ISO-8601"}],"safety_flags":[{"source":"questionnaire|side_effect","level":"critical|warning","code":"text"}]}` |

### New TypeScript types / Pinia stores
```typescript
type SideEffectReportItem = {
  id: string
  severity: 'mild' | 'moderate' | 'severe'
  symptom: string
  note: string | null
  reported_at: string
}

type PatientSafetyFlag = {
  source: 'questionnaire' | 'side_effect'
  level: 'critical' | 'warning'
  code: string
}

type PatientSummary = {
  patient_id: string
  questionnaires: Array<{
    assignment_id: string
    questionnaire_code: 'PHQ-9' | 'GAD-7'
    total_score: number
    has_safety_signal: boolean
    submitted_at: string
  }>
  adherence: Array<{
    id: string
    medication_id: string
    status: 'taken' | 'missed' | 'modified'
    logged_at: string
  }>
  side_effects: SideEffectReportItem[]
  safety_flags: PatientSafetyFlag[]
}

// usePatientSummaryStore — loads doctor-visible patient summary aggregates
// with questionnaire, adherence, side-effects, and derived safety flags
//
// useSideEffectsStore — submits patient side-effect reports and loads
// doctor-visible side-effect history for assigned patients
```

### New env vars (add to `.env.example`)
None

---

## Gate Checks

Run `/phase-gate 05` before committing.

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
def get(url,token):
    req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())
doctor=post("http://localhost:8000/api/v1/auth/login",{"email":"doctor@example.com","password":"changeme123"})
patient=post("http://localhost:8000/api/v1/patients",{"email":f"phase05-smoke-{int(time.time())}@example.com"},doctor["access_token"])
patient_login=post("http://localhost:8000/api/v1/auth/login",{"email":patient["email"],"password":patient["temporary_password"]})
post("http://localhost:8000/api/v1/side-effects",{"severity":"severe","symptom":"Phase 05 smoke symptom","note":"smoke check"},patient_login["access_token"])
summary=get(f"http://localhost:8000/api/v1/patients/{patient['id']}/summary",doctor["access_token"])
print(json.dumps({"side_effects": len(summary.get("side_effects", [])), "safety_flags": len(summary.get("safety_flags", []))}))
PY
# expected: {"side_effects": 1, "safety_flags": 1}

./scripts/phase-gate.sh 05
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
feat(phase-05): add doctor patient summary and safety highlighting
```

---

## Post-Phase Checklist

- [ ] All automated gate checks green
- [ ] All architect review notes resolved
- [ ] `docs/CONTEXT.md` updated — run `/context-update 05`
- [ ] `docs/STATE.md` phase row updated to `✅ done`
- [ ] `docs/CHANGELOG.md` entry added (if CONTEXT.md version bumped)
- [ ] Committed atomically on `feat/phase-05` branch
- [ ] Tag created after merge to develop: `git tag -a v0.5.0 -m "Phase 05: Doctor patient view with recent history and safety highlighting"`
