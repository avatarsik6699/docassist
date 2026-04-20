# Phase Gate

Purpose: run the validation checks for the current phase and produce an honest PASS or FAIL report that includes unresolved architect review notes.

Inputs:

- target phase number, or infer it from `docs/STATE.md`

Required reads:

- `docs/PHASE_XX.md`
- optionally `docs/STATE.md` if no phase number was given

Procedure:

1. Identify the target phase file.
2. Read the phase file's Gate Checks section.
3. Read the phase file's `Architect Review Notes` section and count unchecked items.
4. Ensure a project `.env` exists so Docker Compose and containerized commands use the same credentials the app uses.
5. Start the full Docker Compose stack with `docker compose up -d`.
6. Wait for `db`, `redis`, `backend`, and `frontend` to become healthy, and for `nginx` to be running.
7. Run Alembic migrations inside the backend container so `.env`-backed credentials are used consistently.
8. Run backend tests.
9. Run `pnpm nuxt prepare` so `.nuxt/` types exist for frontend checks.
10. Run frontend type checks.
11. Run frontend unit tests.
12. Run Playwright e2e against the local stack.
13. Run the smoke test from the phase file, or the default health check if none is specified.
14. Produce a table report with one row per check, include the architect review status, and return overall PASS only if automated checks are green and there are no unchecked architect review items.

Rules:

- do not edit files
- do not commit
- do not stop at the first failure; show the full picture
- do use the repository's `.env` when bringing up Docker services or running containerized checks
- do bring up the full stack yourself; the gate should verify the real end-to-end environment, not depend on a manual pre-step
- do not treat unchecked architect review notes as informational; they block PASS until resolved

Preferred command:

```bash
./scripts/phase-gate.sh [XX]
```

If you cannot use the helper script in the current runtime, follow the same sequence manually.

Done when:

- every required check has a reported status
- the output clearly says PASS or FAIL
- any unchecked architect review notes are listed explicitly in the report
