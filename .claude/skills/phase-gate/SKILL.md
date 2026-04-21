---
name: phase-gate
description: Run the current phase gate by following the canonical workflow playbook and the stack-specific commands in docs/STACK.md.
allowed-tools: Bash, Read
argument-hint: "[phase number, e.g. 01]"
---

# phase-gate

Read and follow the canonical playbook:

- `docs/workflows/phase-gate.md`

Supporting command source:

- `docs/STACK.md#gate-commands`

Preferred helper for the reference stack:

- `./scripts/phase-gate.sh [XX]`

Rules:

- use `docs/workflows/phase-gate.md` as the source of truth
- treat `docs/STACK.md#gate-commands` as the authoritative command source
- do not edit files
- do not commit
