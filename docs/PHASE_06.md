# PHASE 06 — [TODO: verify]

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. Be concise. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `06` |
| Title | [TODO: verify] |
| Status | `⏳ pending` |
| Tag | `v0.6.0` |
| Depends on | PHASE_05 gate passing |
| CONTEXT.md version | `v1.6` |

---

## Phase Goal

`docs/SPEC.md` currently defines the recommended MVP phase plan only through `PHASE_05`, so no `PHASE_06` outcome is specified yet. Define the next thin vertical slice in `docs/SPEC.md` and then update this phase contract with exact extracted scope, files, and delivery contracts. [TODO: verify]

---

## Scope

### Backend
- [ ] [TODO: verify]

### Frontend
- [ ] [TODO: verify]

---

## Files

### Create / modify
~~~
[TODO: verify]
~~~

### Do NOT touch
- `docs/SPEC.md`
- `docs/CONTEXT.md`
- `docs/SPEC_POST_MVP.md`

---

## Contracts

> This section is the source of truth for `/context-update`. Fill it in **before** handing to AI.

### New DB tables / columns
[TODO: verify]

### New API endpoints
[TODO: verify]

### New TypeScript types / Pinia stores
[TODO: verify]

### New env vars (add to `.env.example`)
[TODO: verify]

---

## Gate Checks

Run `/phase-gate 06` before committing.

`/phase-gate` returns full PASS only when:
- Automated checks are green
- All architect review items below are resolved (checked off)

Use the commands in [docs/STACK.md](./STACK.md#gate-commands) as the source of truth for:
- infrastructure/bootstrap
- migrations
- backend tests
- frontend prep and typecheck
- frontend unit tests
- e2e
- the default smoke check

If this phase needs a custom smoke target or other phase-specific note, record it here:

```bash
# Optional phase-specific smoke override
curl -s http://localhost:8000/api/v1/[your-endpoint]
# expected: [describe expected response]

# Optional helper for the reference stack
./scripts/phase-gate.sh 06
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
feat(phase-06): [TODO: verify]
```

---

## Post-Phase Checklist

- [ ] All automated gate checks green
- [ ] All architect review notes resolved
- [ ] `docs/CONTEXT.md` updated — run `/context-update 06`
- [ ] `docs/STATE.md` phase row updated to `✅ done`
- [ ] `docs/CHANGELOG.md` entry added (if CONTEXT.md version bumped)
- [ ] Committed atomically on `feat/phase-06` branch
- [ ] Tag created after merge to develop: `git tag -a v0.6.0 -m "Phase 06: [TODO: verify]"`
