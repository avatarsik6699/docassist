---
description: Run the SDD gate checks for a phase. Usage: /phase-gate 01
---

# /phase-gate

Run the repository's gate checks and return an honest PASS/FAIL report.

## Preflight

1. Resolve the phase number from arguments or `docs/STATE.md`.
2. Read `docs/PHASE_XX.md`.
3. Note any phase-specific Gate Checks listed there.
4. Check whether `Architect Review Notes` contains any unchecked items.

## Plan

1. Start the full Docker stack with the repository `.env` and wait for it to become healthy.
2. Run migrations in the backend container, then backend validation, `pnpm nuxt prepare`, frontend type-check, and frontend unit tests.
3. Run Playwright against the local stack.
4. Run the smoke test.
5. Summarize everything in one gate report.
6. Return PASS only if automated checks are green and architect review notes have no unchecked items.

## Commands

Follow the canonical playbook:

- `docs/workflows/phase-gate.md`
- `./scripts/phase-gate.sh [XX]`

Use the matching skill:

- `skills/phase-gate/SKILL.md`

## Verification

Confirm that every expected check produced a result row, even if some failed.

## Summary

Return:

- Docker status
- pytest status
- `nuxt prepare` status
- frontend type-check status
- vitest status
- Playwright status
- smoke test status
- architect review status
- overall PASS/FAIL

## Next Steps

- If PASS: say it is safe to commit.
- If FAIL: list the concrete failing checks or unchecked architect review items and likely fixes.
