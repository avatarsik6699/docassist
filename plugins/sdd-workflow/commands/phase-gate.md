---
description: Run the SDD gate checks for a phase. Usage: /phase-gate 01
---

# /phase-gate

Run the repository's gate checks and return an honest PASS/FAIL report.

## Preflight

1. Resolve the phase number from arguments or `docs/STATE.md`.
2. Read `docs/PHASE_XX.md`.
3. Read `docs/STACK.md#gate-commands`.
4. Check whether `Architect Review Notes` contains any unchecked items.

## Plan

1. Follow the gate procedure in `docs/workflows/phase-gate.md`.
2. Use `docs/STACK.md#gate-commands` as the command source for the standard checks.
3. If available, use `./scripts/phase-gate.sh [XX]` as the reference-stack helper.
4. Return PASS only if automated checks are green and architect review notes have no unchecked items.

## Commands

Follow the canonical playbook:

- `docs/workflows/phase-gate.md`
- `docs/STACK.md#gate-commands`
- `./scripts/phase-gate.sh [XX]`

Use the matching skill:

- `skills/phase-gate/SKILL.md`

## Verification

Confirm that every expected check produced a result row, even if some failed.

## Summary

Return:

- Docker status
- pytest status
- frontend prep status
- frontend type-check status
- vitest status
- Playwright status
- smoke test status
- architect review status
- overall PASS/FAIL
