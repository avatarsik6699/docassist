---
name: phase-gate
description: Run the full SDD gate for a phase by following the canonical workflow playbook and stack gate command table.
metadata:
  priority: 5
  pathPatterns:
    - 'docs/PHASE_*.md'
    - 'docs/STATE.md'
    - 'docs/STACK.md'
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

Canonical playbook:

- `docs/workflows/phase-gate.md`

Stack command source:

- `docs/STACK.md#gate-commands`

Preferred helper:

- `./scripts/phase-gate.sh [XX]`

Rules:

- follow the workflow doc exactly
- treat `docs/STACK.md` as authoritative for commands
- do not edit code
- do not commit
