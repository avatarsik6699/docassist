# CHANGELOG — Spec & Architecture History

> Records changes to `docs/SPEC.md` and `docs/CONTEXT.md`. This is **NOT** a git commit log.
> Purpose: capture *why* the contract changed and which phases were affected.
> Format: newest entry at top.

---

## v1.0 — 2026-04-20 — SPEC Reset For Current Template

**Type**: spec-change
**Author**: Codex
**Triggered by**: Derived project still used an older, implementation-heavy spec format after the template evolved

### Changes
- `SPEC.md` was rewritten to match the current template intent: product problem, users, MVP scope, rules, constraints, and release strategy
- MVP scope was reduced to the core psychiatry monitoring loop instead of the broader platform vision
- Deferred functionality was preserved in new file `docs/SPEC_POST_MVP.md` instead of being removed

### Affected Phases
- None yet; no concrete `PHASE_XX.md` files exist in this repository

### Contract Updates
- `CONTEXT.md` unchanged
- No implementation contract was asserted by this doc-only reset

### Notes
The old spec contained many details that belong in architecture, testing, or later phase contracts rather than the product spec itself.

---

## v1.0 — [DATE] — Initial Template

**Type**: initial-setup
**Author**: [OWNER]
**Triggered by**: Project initialization from sdd-template

### Changes
- `SPEC.md` created: project goals, roles, data model, API endpoints, phase plan
- `CONTEXT.md` v1.0 created: initial stack snapshot, core models, active endpoints
- `PHASE_01.md` created: Foundation scope defined

### Affected Phases
- None (initial state)

### Contract Updates
- `CONTEXT.md` initialized at `v1.0`

---

<!--
ENTRY TEMPLATE — copy this block when adding a new entry:

## [CONTEXT_VERSION] — [YYYY-MM-DD] — [Short Title]

**Type**: spec-change | arch-decision | breaking-change | phase-completion | addendum
**Author**: [name / AI skill]
**Triggered by**: [What caused this? User request, bug discovery, new requirement, etc.]

### Changes
- [bullet: what specifically changed in SPEC.md or the architecture]

### Affected Phases
- PHASE_XX — [why it is affected]

### Contract Updates
- `CONTEXT.md` bumped from `vX.Y` to `vX.Z`
- [list schema / endpoint / type changes]

### Notes
[Trade-offs, decisions, context not captured elsewhere]

-->
