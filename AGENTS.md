# Global Agent Rules

## What Is Portable Here

This repository contains two layers of agent guidance:

- `AGENTS.md` files: model-agnostic rules intended for any capable coding agent
- `CLAUDE.md` and `.claude/skills/`: Claude Code specific adapters, slash commands, and tool policies

When both exist, prefer this file for shared process rules and treat Claude-specific files as optional automation on top.

## Template Repo Scope

This repository is the template itself, not an active product.

- Do not treat `docs/` as live requirements. They are template files with placeholders.
- Only make changes that improve the template for future projects.
- Keep references consistent across `README.md`, `CLAUDE.md`, `AGENTS.md`, `human-instructions/`, `docs/workflows/`, `.claude/skills/`, and `plugins/sdd-workflow/`.

## Repo Memory Files

Keep lightweight project memory in repository docs so different agent runtimes can recover the same high-signal context across sessions.

Recommended files:
- `docs/DECISIONS.md` for ADR-style technical decisions
- `docs/KNOWN_GOTCHAS.md` for recurring pitfalls, edge cases, and local-environment traps

Keep these files concise and current. Prefer updating them over relying on conversational memory.

## Library Documentation Lookup

When maintaining the template or reference implementation, use up-to-date documentation for external libraries instead of relying on stale model memory alone.

For derived projects, the canonical runtime rule lives in `human-instructions/AGENTS.for-new-projects.md`.

## Skills And Protocols

The workflow protocols in `docs/workflows/` are the canonical, model-agnostic playbooks for this template. Agent-specific skill wrappers should point to them instead of duplicating the full procedures.

Portable interpretation:
- `spec-sync`: protocol for propagating `docs/SPEC.md` changes
- `phase-init`: protocol for scaffolding a new `docs/PHASE_XX.md`
- `phase-gate`: protocol for running the current stack's gate checks from `docs/STACK.md` and failing if `Architect Review Notes` still contain unchecked items
- `context-update`: protocol for syncing `docs/CONTEXT.md`, `docs/STATE.md`, and `docs/CHANGELOG.md`

If an agent runtime does not support native slash commands or skills, execute the corresponding markdown procedure manually from `docs/workflows/`.
