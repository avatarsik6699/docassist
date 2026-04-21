# Agent Setup Once

This document captures one-time setup guidance for docs lookup integrations used by this template. It is not a runtime rules file.

## Documentation Lookup Setup

Preferred docs lookup order for third-party libraries and frameworks:

1. `Context7` via MCP, if the current runtime supports MCP and the server is configured
2. `ctx7` CLI via `npx ctx7@latest ...`
3. Official library documentation or other primary-source docs

For OpenAI products and platform features, prefer the official OpenAI developer docs MCP server when available.

## Example MCP Setup

### Claude Code

```json
{
  "mcpServers": {
    "context7": {
      "command": "/home/USER/.nvm/versions/node/vX.Y.Z/bin/context7-mcp"
    }
  }
}
```

### Codex

```bash
codex mcp add context7 -- /home/USER/.nvm/versions/node/vX.Y.Z/bin/context7-mcp
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

Useful follow-up commands:

```bash
codex mcp list
codex mcp get context7
codex mcp get openaiDeveloperDocs
```

Restart the runtime after MCP config changes so new servers are available in fresh sessions.

## CLI Fallback

If MCP is unavailable in the current runtime, use:

```bash
npx ctx7@latest library "<library name>" "<question>"
npx ctx7@latest docs /org/project "<question>"
```

Rules:

- resolve the library ID with `library` first unless the `/org/project` ID is already known
- use the official library name with correct punctuation
- do not send secrets in queries
- if you hit quota or auth limits, run `npx ctx7@latest login` or set `CONTEXT7_API_KEY`
