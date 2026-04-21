# CHANGELOG — Spec & Architecture History

> Records changes to `docs/SPEC.md` and `docs/CONTEXT.md`. This is **NOT** a git commit log.
> Purpose: capture *why* the contract changed and which phases were affected.
> Format: newest entry at top.

---

## v1.3 — 2026-04-21 — Phase 02 Contract Synced

**Type**: phase-completion
**Author**: Codex (`/context-update`)
**Triggered by**: Phase 02 implementation landed and the doctor-patient onboarding contract became active

### Changes
- Added the doctor-patient relationship contract to the shared repository memory
- Recorded the active patient roster API surface for doctor-managed create, list, activate, and patient setup-account flows
- Captured the new authenticated UI surface for doctor roster management and patient first-login onboarding
- Advanced the schema snapshot to Alembic head `0002_doctor_patient_profiles`

### Affected Phases
- PHASE_02 — implementation synchronized into the shared contract snapshot after a passing gate and manual verification

### Contract Updates
- `CONTEXT.md` bumped from `v1.2` to `v1.3`
- Added `DoctorProfile` and `PatientProfile` to the active core model snapshot
- Appended the `/api/v1/patients` and `/api/v1/patients/setup-account` endpoints plus the `/patients` and `/setup-account` frontend routes

### Notes
This is an additive bump because Phase 02 extends the active contract without replacing the Phase 01 surface. The phase gate is green, though the current phase-specific smoke command still only checks that the roster endpoint responds rather than asserting a doctor-authenticated payload.

## v1.2 — 2026-04-20 — Phase 01 Contract Synced

**Type**: breaking-change
**Author**: Codex (`/context-update`)
**Triggered by**: Phase 01 implementation landed and replaced stale template contract details in `CONTEXT.md`

### Changes
- Synced the Phase 01 foundation contract for the live template repository
- Confirmed the `users` model now uses the real role taxonomy: `admin`, `doctor`, `patient`
- Locked in the active auth surface: health check, login, current-user lookup, and logout stub
- Recorded the seeded admin account and active Nuxt auth shell as part of the repository memory

### Affected Phases
- PHASE_01 — implementation synchronized into the shared contract snapshot; phase closure still blocked by failing E2E expectations

### Contract Updates
- `CONTEXT.md` bumped from `v1.0` to `v1.2`
- Replaced the stale template role enum in `core_models`
- Refreshed phase pointers and repository notes to reflect the shipped foundation

### Notes
The version bump is breaking rather than additive because the previous `CONTEXT.md` snapshot still described placeholder role values from the template instead of the implemented Phase 01 contract. The current gate blocker is in Playwright, where two tests still expect the login submit button to be enabled before form input is provided.

## v1.0 — 2026-04-20 — SPEC Reset For Current Template

**Type**: spec-change
**Author**: Codex
**Triggered by**: Derived project still used an older, implementation-heavy spec format after the template evolved

### Changes
- `SPEC.md` was rewritten to match the current template intent: product problem, users, MVP scope, rules, constraints, and release strategy
- MVP scope was reduced to the core psychiatry monitoring loop instead of the broader platform vision
- Deferred functionality was preserved in new file `docs/SPEC_POST_MVP.md` instead of being removed

### Affected Phases
- None yet; no concrete `PHASE_XX.md` files exist in this repository

### Contract Updates
- `CONTEXT.md` unchanged
- No implementation contract was asserted by this doc-only reset

### Notes
The old spec contained many details that belong in architecture, testing, or later phase contracts rather than the product spec itself.

---

## v1.0 — [DATE] — Initial Template

**Type**: initial-setup
**Author**: [OWNER]
**Triggered by**: Project initialization from sdd-template

### Changes
- `SPEC.md` created: project goals, roles, data model, API endpoints, phase plan
- `CONTEXT.md` v1.0 created: initial stack snapshot, core models, active endpoints
- `PHASE_01.md` created: Foundation scope defined

### Affected Phases
- None (initial state)

### Contract Updates
- `CONTEXT.md` initialized at `v1.0`

---

<!--
ENTRY TEMPLATE — copy this block when adding a new entry:

## [CONTEXT_VERSION] — [YYYY-MM-DD] — [Short Title]

**Type**: spec-change | arch-decision | breaking-change | phase-completion | addendum
**Author**: [name / AI skill]
**Triggered by**: [What caused this? User request, bug discovery, new requirement, etc.]

### Changes
- [bullet: what specifically changed in SPEC.md or the architecture]

### Affected Phases
- PHASE_XX — [why it is affected]

### Contract Updates
- `CONTEXT.md` bumped from `vX.Y` to `vX.Z`
- [list schema / endpoint / type changes]

### Notes
[Trade-offs, decisions, context not captured elsewhere]

-->
