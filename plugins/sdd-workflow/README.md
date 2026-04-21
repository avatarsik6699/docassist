# SDD Workflow Codex Plugin

This plugin makes the repository's SDD workflow visible to Codex as native:

- skills under `skills/`
- slash commands under `commands/`
- project-local MCP expectations via `.mcp.json`
- safety/format hooks via `hooks.json`

## What this adds

- `/phase-init`
- `/phase-gate`
- `/context-update`
- `/spec-sync`

The plugin mirrors the existing Claude setup in `.claude/skills/`, but both layers are wrappers around the canonical workflow docs in [docs/workflows/](../../docs/workflows/README.md).

## Documentation lookup

Project runtime rules live in [AGENTS.md](../../AGENTS.md). One-time MCP and CLI setup guidance lives in [human-instructions/agent_setup_once.md](../../human-instructions/agent_setup_once.md).

The plugin declares a project-local `context7` MCP server in [`.mcp.json`](./.mcp.json). In this workspace, Codex may also have a global MCP entry configured, which is often the most reliable option when the local `context7-mcp` binary is not on PATH.

## Restart requirement

After adding or changing plugin files, restart Codex in this workspace so the plugin, slash commands, and marketplace entry are reloaded.
