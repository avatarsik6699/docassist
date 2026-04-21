# Template Repo Claude Adapter

Read [AGENTS.md](AGENTS.md) first. It is the source of truth for the shared rules used to maintain this template.

## Template Repo Guardrails

- This repository is the template, not a live product.
- Do not treat `docs/` as active requirements; placeholders are intentional.
- Do not run derived-project workflows here unless you are explicitly testing those workflows.

## Skill Testing

- When testing `/phase-init`, `/phase-gate`, `/context-update`, or `/spec-sync`, use a scratch directory or a derived-project copy.
- Do not mutate this repo's template `docs/` as if they were project state.

## Claude-Specific Notes

- Claude slash commands map to the workflow playbooks in `docs/workflows/`.
- Claude skill wrappers live under `.claude/skills/`.
- Keep references aligned across `AGENTS.md`, `README.md`, `human-instructions/`, `docs/workflows/`, and `.claude/skills/` whenever the pipeline changes.
