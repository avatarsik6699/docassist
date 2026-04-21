---
name: context-update
description: Synchronize CONTEXT, STATE, and CHANGELOG after a completed phase by following the canonical workflow playbook.
allowed-tools: Read, Write, Edit, Glob
argument-hint: "[phase number, e.g. 01]"
---

# context-update

Read and follow the canonical playbook:

- `docs/workflows/context-update.md`

Inputs:

- target phase number from `$ARGUMENTS`

Rules:

- use `docs/workflows/context-update.md` as the source of truth
- do not duplicate or invent workflow steps that are not in the playbook
- do not commit automatically
