# CHANGELOG — Spec & Architecture History

> Records changes to `docs/SPEC.md` and `docs/CONTEXT.md`. This is **NOT** a git commit log.
> Purpose: capture *why* the contract changed and which phases were affected.
> Format: newest entry at top.

---

## v1.1 — 2026-04-25 — Backend Restructured to Modular DDD

**Type**: arch-decision
**Author**: AI agent (Claude)
**Triggered by**: Architect request to replace the layered `api/core/db/services/schemas` layout with bounded contexts before further endpoints land.

### Changes
- `SPEC.md` §4.1 rewritten: backend layout is now `app/{core,db,shared}/` + `app/modules/<name>/` + `app/api/v1/router.py`, with explicit layering and import rules.
- New backend layout in code: `app/modules/users/` (owns `User`, `UserRole`, `UserService`, `UserRepository`), `app/modules/auth/` (owns JWT utils, `AuthService`, `get_current_user`, `require_role`), `app/modules/health/`.
- Service + repository layers introduced; route handlers no longer issue SQL or hash passwords directly.
- Old paths removed: `app/api/v1/{auth,health}.py`, `app/db/models/`, `app/schemas/`, `app/core/auth.py`. The duplicate `Role` enum is gone — `users.UserRole` is the single source of truth.
- `app/core/` split into `config.py`, `constants.py`, `exceptions.py` (`AppException` base), `logging.py`, `middleware.py`.
- Domain exceptions inherit from `AppException` (subclass of `HTTPException`); FastAPI renders status/headers automatically.
- `alembic/env.py` now imports `app.modules.users` to register ORM metadata.
- `docs/PHASE_01.md` removed — the phase had not started and SPEC was not yet finalised.

### Affected Phases
- All future phases — module layout is the new baseline. New domains (documents, sessions, notifications, …) must be added as `app/modules/<name>/` with the standard internal layout.

### Contract Updates
- `CONTEXT.md` bumped from `v1.0` to `v1.1` (minor — backend structure breaking change for code, but REST contract unchanged).
- REST endpoints unchanged: `GET /api/v1/health`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`.
- DB schema unchanged (single `users` table, migration `0001_users_table` still head).

### Notes
- Module boundaries are enforced by convention + code review, not import-linter (decision deferred until repeated violations appear).
- `auth → users` is the only cross-module dependency today. Reverse direction is forbidden.
- Tests updated to import `User`, `UserRole` from `app.modules.users` and JWT helpers from `app.modules.auth`.

---

## v1.0 — 2026-04-24 — Frontend UI Baseline Standardized

**Type**: arch-decision
**Author**: AI agent (Codex)
**Triggered by**: Request to standardize component system, dark theme, and i18n stack

### Changes
- Updated `SPEC.md` frontend section to remove stale Vue/Pinia placeholders and define React Router + shadcn baseline.
- Updated `STACK.md` and `frontend/README.md` with the concrete UI stack and shadcn AI workflow commands.
- Added decision record in `DECISIONS.md` for UI baseline (`shadcn/ui`, Tailwind v4, `next-themes`, `react-i18next`, React Query).
- Added shadcn skills/MCP setup notes into `AGENT_SETUP.md`.

### Affected Phases
- PHASE_01 — frontend foundation now explicitly includes UI baseline initialization.

### Contract Updates
- No backend/API/DB contract changes.
- No `CONTEXT.md` version bump required.

### Notes
- This is a frontend architecture alignment update; data and API contracts are unchanged.

## v0.1.0 — 2026-04-24 — First Published Template Release

**Type**: addendum
**Author**: template-maintainer
**Triggered by**: Template repository release cut for namespaced workflow/template tags

### Changes
- Published template release coordinate: `template/fastapi-react-router/v0.1.0`
- Published compatible workflow coordinate: `workflow/v0.1.0`
- Added released-artifact validation/status flow for maintainers
- Hardened upgrade baseline integrity by ignoring local `.claude/settings.local.json`

### Affected Phases
- None (template maintainer release surface)

### Contract Updates
- No SPEC/CONTEXT schema change; release metadata and upgrade behavior hardened

### Notes
- This entry documents template release readiness for generated projects based on tagged artifacts.

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
