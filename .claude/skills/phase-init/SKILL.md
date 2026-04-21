---
name: phase-init
description: Scaffold a new PHASE_XX.md by following the canonical workflow playbook.
allowed-tools: Read, Write, Glob
argument-hint: "[phase number, e.g. 02]"
---

# phase-init

Read and follow the canonical playbook:

- `docs/workflows/phase-init.md`

Inputs:

- target phase number from `$ARGUMENTS`

Rules:

- use `docs/workflows/phase-init.md` as the source of truth
- never modify `docs/SPEC.md`
- never modify `docs/CONTEXT.md`
- do not commit automatically
