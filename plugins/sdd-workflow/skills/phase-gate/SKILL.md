---
name: phase-gate
description: Run the full SDD gate for a phase: infrastructure checks, tests, e2e, smoke verification, and architect review notes verification. Use when the user asks whether a phase is ready to commit.
metadata:
  priority: 5
  pathPatterns:
    - 'docs/PHASE_*.md'
    - 'docs/STATE.md'
    - 'frontend/playwright.config.ts'
    - 'frontend/test-results/**'
    - 'frontend/playwright-report/**'
    - 'docker-compose.yml'
  bashPatterns:
    - '\bdocker compose\b'
    - '\bpytest\b'
    - '\bpnpm\b'
    - '\bvitest\b'
  promptSignals:
    phrases:
      - "phase gate"
      - "run gate checks"
      - "ready to commit"
      - "check phase readiness"
    allOf:
      - [phase, gate]
      - [gate, checks]
    anyOf:
      - "pytest"
      - "typecheck"
      - "playwright"
    noneOf: []
    minScore: 6
retrieval:
  aliases:
    - sdd gate
    - phase verification
  intents:
    - verify a phase before commit
    - run project gate checks
  entities:
    - docker compose
    - pytest
    - vitest
    - playwright
---

# phase-gate

Canonical portable playbook: `docs/workflows/phase-gate.md`

Use this skill when the user wants an honest PASS/FAIL view of the current phase.

Workflow:

1. Resolve the target phase from arguments or from `docs/STATE.md`.
2. Read the phase file's Gate Checks section and `Architect Review Notes`.
3. Check Docker infrastructure state.
4. Start the full Docker stack and wait for health.
5. Run migrations inside the backend container so `.env`-backed credentials are used.
6. Run backend tests.
7. Run `pnpm nuxt prepare` so `.nuxt/` types exist.
8. Run frontend type checks.
9. Run frontend unit tests.
10. Run Playwright end-to-end tests against the local stack.
11. Run the smoke check.
12. Mark architect review as failed if any checklist item in `Architect Review Notes` is still unchecked.
13. Produce a structured gate report with PASS/FAIL and exact failing areas.

Rules:

- Do not edit code.
- Do not commit.
- Do not hide failures behind early exit when later checks can still provide useful signal.
- Do not return PASS while unchecked architect review notes remain.
- Prefer `./scripts/phase-gate.sh [XX]` when possible.
