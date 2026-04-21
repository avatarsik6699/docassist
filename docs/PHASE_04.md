# PHASE 04 — Questionnaire assignment, submission, and scoring for `PHQ-9` and `GAD-7`

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. Be concise. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `04` |
| Title | Questionnaire assignment, submission, and scoring for `PHQ-9` and `GAD-7` |
| Status | `⏳ pending` |
| Tag | `v0.4.0` |
| Depends on | PHASE_03 gate passing |
| CONTEXT.md version | `v1.4` |

---

## Phase Goal

This phase implements the next MVP outcome from `docs/SPEC.md`: a doctor assigns one or more supported questionnaires, and a patient completes those questionnaires from the web app with validated scoring for `PHQ-9` and `GAD-7`. It should extend the existing doctor-patient workflow with auditable questionnaire assignments, stored raw answers, and total scores so later phases can present recent history and safety signals in the doctor view without rebuilding the data model.

---

## Scope

### Backend
- [ ] Add questionnaire assignment and response models so the product can store assigned `PHQ-9` and `GAD-7` questionnaires, raw answers, total scores, and completion state
- [ ] Implement doctor-only APIs to assign supported questionnaires to an assigned patient and review assignment status needed for ongoing care workflows
- [ ] Implement patient-only APIs to list pending questionnaires and submit completed `PHQ-9` and `GAD-7` responses
- [ ] Add backend validation and scoring rules so questionnaire scoring follows the validated scoring model and stores any explicit safety-answer flag needed by later phases

### Frontend
- [ ] Add a doctor workflow in the authenticated app to assign `PHQ-9` and `GAD-7` to a patient from the existing roster context
- [ ] Add a patient workflow to view pending questionnaires and complete them from the web app on mobile and desktop
- [ ] Show questionnaire completion state and recorded scores in the phase-owned UI surfaces needed to support assignment and submission without building the full doctor summary planned for Phase 05

---

## Files

### Create / modify
~~~
alembic/versions/0004_questionnaire_assignments_and_responses.py
app/api/v1/questionnaires.py
app/db/base.py
app/db/models/questionnaire_assignment.py
app/db/models/questionnaire_response.py
app/main.py
app/schemas/questionnaires.py
frontend/app/features/questionnaires/model/questionnaire-store.ts
frontend/app/features/questionnaires/ui/doctor-questionnaire-assignment-form.vue
frontend/app/features/questionnaires/ui/patient-questionnaire-list.vue
frontend/app/features/questionnaires/ui/questionnaire-form.vue
frontend/app/pages/dashboard.vue
frontend/app/pages/patients.vue
frontend/app/pages/questionnaires/[assignmentId].vue
frontend/app/shared/types/schema.ts
tests/conftest.py
tests/test_questionnaires_api.py
frontend/tests/questionnaire-store.test.ts
frontend/tests/e2e/questionnaire-submission.spec.ts
~~~

### Do NOT touch
- `docs/SPEC.md`
- `docs/CONTEXT.md`
- `docs/SPEC_POST_MVP.md`
- Side-effect reporting, doctor patient summary, and broader safety-highlighting features planned for later phases

---

## Contracts

> This section is the source of truth for `/context-update`. Fill it in **before** handing to AI.

### New DB tables / columns
~~~
questionnaire_assignments(
  id UUID PK,
  patient_user_id UUID NOT NULL REFERENCES users(id),
  doctor_user_id UUID NOT NULL REFERENCES users(id),
  questionnaire_code TEXT NOT NULL,
  status TEXT NOT NULL,
  assigned_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)

questionnaire_responses(
  id UUID PK,
  assignment_id UUID NOT NULL REFERENCES questionnaire_assignments(id),
  patient_user_id UUID NOT NULL REFERENCES users(id),
  questionnaire_code TEXT NOT NULL,
  answers JSONB NOT NULL,
  total_score INTEGER NOT NULL,
  has_safety_signal BOOLEAN NOT NULL,
  submitted_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL
)
~~~

### New API endpoints
| Method | Path | Auth | Response |
|--------|------|------|----------|
| `GET` | `/api/v1/patients/{patient_id}/questionnaires` | JWT doctor | `{"items":[{"id":"uuid","questionnaire_code":"PHQ-9|GAD-7","status":"assigned|completed","assigned_at":"ISO-8601","completed_at":"ISO-8601|null"}]}` |
| `POST` | `/api/v1/patients/{patient_id}/questionnaires` | JWT doctor | `{"id":"uuid","patient_user_id":"uuid","doctor_user_id":"uuid","questionnaire_code":"PHQ-9|GAD-7","status":"assigned","assigned_at":"ISO-8601"}` |
| `GET` | `/api/v1/questionnaires/pending` | JWT patient | `{"items":[{"id":"uuid","questionnaire_code":"PHQ-9|GAD-7","status":"assigned","assigned_at":"ISO-8601"}]}` |
| `POST` | `/api/v1/questionnaires/{assignment_id}/submit` | JWT patient | `{"id":"uuid","assignment_id":"uuid","questionnaire_code":"PHQ-9|GAD-7","total_score":0,"has_safety_signal":false,"submitted_at":"ISO-8601"}` |

### New TypeScript types / Pinia stores
```typescript
type QuestionnaireAssignmentItem = {
  id: string
  questionnaire_code: 'PHQ-9' | 'GAD-7'
  status: 'assigned' | 'completed'
  assigned_at: string
  completed_at: string | null
}

type QuestionnaireSubmissionResult = {
  id: string
  assignment_id: string
  questionnaire_code: 'PHQ-9' | 'GAD-7'
  total_score: number
  has_safety_signal: boolean
  submitted_at: string
}

// useQuestionnaireStore — loads doctor-visible questionnaire assignments for a patient,
// assigns supported questionnaires, loads patient pending questionnaires, and submits
// completed responses while refreshing assignment state after mutations
```

### New env vars (add to `.env.example`)
None

---

## Gate Checks

Run `/phase-gate 04` before committing.

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
patient=post("http://localhost:8000/api/v1/patients",{"email":f"phase04-smoke-{int(time.time())}@example.com"},doctor["access_token"])
assignment=post(f"http://localhost:8000/api/v1/patients/{patient['id']}/questionnaires",{"questionnaire_code":"PHQ-9"},doctor["access_token"])
patient_login=post("http://localhost:8000/api/v1/auth/login",{"email":patient["email"],"password":patient["temporary_password"]})
submission=post(f"http://localhost:8000/api/v1/questionnaires/{assignment['id']}/submit",{"answers":{"q1":0,"q2":0,"q3":0,"q4":0,"q5":0,"q6":0,"q7":0,"q8":0,"q9":0}},patient_login["access_token"])
print(json.dumps({"questionnaire_code": submission["questionnaire_code"], "total_score": submission["total_score"]}))
PY
# expected: {"questionnaire_code": "PHQ-9", "total_score": 0}

./scripts/phase-gate.sh 04
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
feat(phase-04): add questionnaire assignment, submission, and scoring
```

---

## Post-Phase Checklist

- [ ] All automated gate checks green
- [ ] All architect review notes resolved
- [ ] `docs/CONTEXT.md` updated — run `/context-update 04`
- [ ] `docs/STATE.md` phase row updated to `✅ done`
- [ ] `docs/CHANGELOG.md` entry added (if CONTEXT.md version bumped)
- [ ] Committed atomically on `feat/phase-04` branch
- [ ] Tag created after merge to develop: `git tag -a v0.4.0 -m "Phase 04: Questionnaire assignment, submission, and scoring for PHQ-9 and GAD-7"`
