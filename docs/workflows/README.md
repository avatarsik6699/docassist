# Workflow Playbooks

These files are the canonical, model-agnostic workflow procedures for the SDD pipeline.

Agent-specific wrappers should point here rather than duplicate the full instructions.

Use these playbooks when:

- the agent runtime does not support native slash skills
- you want one canonical workflow that multiple agents can follow
- you want to review or refine the process without editing agent-specific wrappers first

Available playbooks:

- [phase-init.md](./phase-init.md)
- [phase-gate.md](./phase-gate.md)
- [context-update.md](./context-update.md)
- [spec-sync.md](./spec-sync.md)
