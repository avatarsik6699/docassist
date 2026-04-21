---
name: phase-init
description: Initialize a new SDD phase document from SPEC, CONTEXT, STATE, and PHASE_TEMPLATE. Use when the user wants to scaffold or refresh a PHASE_XX.md file.
metadata:
  priority: 5
  pathPatterns:
    - 'docs/PHASE_TEMPLATE.md'
    - 'docs/PHASE_*.md'
    - 'docs/SPEC.md'
    - 'docs/STATE.md'
    - 'docs/CONTEXT.md'
  promptSignals:
    phrases:
      - "phase init"
      - "initialize phase"
      - "create phase doc"
      - "scaffold phase"
    allOf:
      - [phase, init]
      - [phase, scaffold]
    anyOf:
      - "phase"
      - "phase document"
      - "phase file"
    noneOf: []
    minScore: 6
retrieval:
  aliases:
    - sdd phase init
    - phase bootstrap
  intents:
    - create a phase document
    - scaffold next phase
  entities:
    - PHASE_TEMPLATE.md
    - SPEC.md
    - STATE.md
---

# phase-init

Canonical playbook:

- `docs/workflows/phase-init.md`

Rules:

- follow the workflow doc exactly
- do not modify `docs/SPEC.md`
- do not modify `docs/CONTEXT.md`
- do not commit
