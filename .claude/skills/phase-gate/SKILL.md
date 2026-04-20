---
name: phase-gate
description: Run all gate checks for the current phase before committing. Starts the Docker stack, uses the repository .env, checks migrations, pytest, Nuxt prepare, frontend type-checks, vitest, Playwright e2e, a smoke endpoint, and unresolved architect review notes. Reports PASS or FAIL.
allowed-tools: Bash, Read
argument-hint: "[phase number, e.g. 01]"
---

> **Before generating code for any library (FastAPI, Nuxt, SQLAlchemy, Pydantic, etc.),
> follow the `ctx7` documentation-lookup rule in `CLAUDE.md`. Stale API knowledge is
> the #1 source of rework in this workflow.**

> Canonical portable playbook: `docs/workflows/phase-gate.md`

You are running the SDD phase gate checks. Your job is to run all required checks and produce an honest PASS / FAIL report. Do NOT modify any code files — this skill is read-only.

**Target phase**: $ARGUMENTS

## Step 1 — Identify the phase file

If `$ARGUMENTS` is provided, read `docs/PHASE_$ARGUMENTS.md`.
If no argument, read `docs/STATE.md` and find the phase with status `🔄 in-progress`. Then read that phase file.
If neither resolves, ask: "Which phase number should I check? (e.g. /phase-gate 01)"

## Step 2 — Read gate commands and architect review notes

From the "Gate Checks" section of the phase file, note:
- Any smoke test URL and expected response
- Any phase-specific commands beyond the standard set

From the `Architect Review Notes` section of the phase file, collect every unchecked checklist item.
Treat each unchecked item as an open issue that blocks PASS until it is resolved and checked off.

## Step 3 — Check infrastructure

```bash
docker compose up -d
```

Use the repository `.env` as the source of truth for Docker Compose and containerized commands.
Wait until `db`, `redis`, `backend`, and `frontend` are healthy, and `nginx` is running.
If the stack fails to become ready after a reasonable timeout, report ❌ and stop.

## Step 4 — Run migrations inside the backend container

```bash
docker compose exec -T backend uv run alembic upgrade head
```

If this fails: record ❌ and continue.

## Step 5 — Run backend tests

```bash
uv run pytest tests/ -v 2>&1
```

Capture full output. Count passed / failed / error.
If ANY test fails or errors: record ❌, note the failing test names. Do NOT stop — continue to next checks so the full picture is visible.

## Step 6 — Generate Nuxt types

```bash
cd frontend && pnpm nuxt prepare 2>&1
```

If this fails: record ❌ and continue. Frontend type-check and Vitest depend on `.nuxt/`.

## Step 7 — Run TypeScript check

```bash
cd frontend && pnpm typecheck 2>&1
```

Count errors. If any errors: record ❌ with error count.

## Step 8 — Run frontend tests

```bash
cd frontend && pnpm test 2>&1
```

Count passed / failed. If any fail: record ❌.

## Step 9 — Run Playwright end-to-end tests

With the stack healthy, run:

```bash
cd frontend && pnpm test:e2e 2>&1
```

After the run, parse `frontend/test-results/junit.xml` for pass/fail/skip counts (the junit reporter is configured in `frontend/playwright.config.ts`). On any failure, note which spec files failed and include the path to the HTML report (`frontend/playwright-report/index.html`) so the user can open it.

If `frontend/test-results/junit.xml` is missing after the run, record ❌ with the note "Playwright did not emit junit.xml — check reporter config" and move on.

## Step 10 — Run smoke test

Run the `curl` command from the phase file's Gate Checks section. If no smoke test is listed, use:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health
```
Expected: HTTP 200. If backend is not running, report ❌ with note "backend not running".

## Step 11 — Produce gate report

Output in this exact format:

```
## Phase Gate Report — PHASE_[XX]

| Check          | Status | Details                    |
|----------------|--------|----------------------------|
| Infrastructure | ✅/❌  | full stack healthy/running |
| Migrations     | ✅/❌  | ran inside backend container |
| pytest         | ✅/❌  | N passed, M failed         |
| nuxt prepare   | ✅/❌  | generated `.nuxt` / error  |
| typecheck      | ✅/❌  | N errors                   |
| vitest         | ✅/❌  | N passed, M failed         |
| e2e (playwright)| ✅/❌  | N passed, M failed — report: frontend/playwright-report/index.html |
| Smoke test     | ✅/❌  | HTTP NNN                   |
| Architect review | ✅/❌ | no open items / N unchecked items |

**Overall: ✅ PASS / ❌ FAIL**
```

If architect review is ❌, list each unchecked item verbatim under an `Open architect review notes` heading.

If **PASS**: confirm it is safe to commit with the atomic commit message from the phase file.

If **FAIL**: list each failed check with the specific error output. Also list unchecked architect review notes if any remain. Do NOT suggest committing. Suggest fixes where obvious.

## Rules
- Do not run `docker compose down` or any destructive command
- Do not edit any files
- Do not commit
- Report every check even if a previous one failed — give the full picture
- Do not return PASS while any architect review checklist item remains unchecked
- Prefer `./scripts/phase-gate.sh [XX]` when the runtime can execute repository scripts directly
