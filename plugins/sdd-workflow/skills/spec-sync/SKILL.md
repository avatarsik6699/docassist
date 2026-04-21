---
name: spec-sync
description: Propagate SPEC.md changes into the rest of the SDD documentation set. Use when the system spec has changed and downstream contracts may now be stale.
metadata:
  priority: 5
  pathPatterns:
    - 'docs/SPEC.md'
    - 'docs/CONTEXT.md'
    - 'docs/STATE.md'
    - 'docs/CHANGELOG.md'
    - 'docs/PHASE_*.md'
  promptSignals:
    phrases:
      - "spec sync"
      - "sync after spec change"
      - "spec changed"
      - "prevent context drift"
    allOf:
      - [spec, sync]
      - [spec, changed]
    anyOf:
      - "context drift"
      - "phase review"
      - "contract update"
    noneOf: []
    minScore: 6
retrieval:
  aliases:
    - sync spec change
    - update phases after spec edit
  intents:
    - propagate a spec change
    - mark affected phases for review
  entities:
    - SPEC.md
    - CONTEXT.md
    - PHASE files
---

# spec-sync

Canonical playbook:

- `docs/workflows/spec-sync.md`

Rules:

- follow the workflow doc exactly
- never rewrite a phase file from scratch
- do not commit
