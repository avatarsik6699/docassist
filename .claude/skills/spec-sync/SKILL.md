---
name: spec-sync
description: Propagate SPEC.md changes by following the canonical workflow playbook.
allowed-tools: Read, Write, Edit, Glob, Bash
argument-hint: "[brief description of what changed in SPEC.md]"
---

# spec-sync

Read and follow the canonical playbook:

- `docs/workflows/spec-sync.md`

Inputs:

- change description from `$ARGUMENTS`

Rules:

- use `docs/workflows/spec-sync.md` as the source of truth
- preserve historical changelog entries
- do not commit automatically
