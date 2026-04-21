# Frontend

Nuxt 4 SPA with **Feature-Sliced Design (FSD)** architecture, Tailwind CSS, Nuxt UI, Pinia, and i18n.

---

## Architecture: Feature-Sliced Design

The `app/` directory follows [FSD](https://feature-sliced.design/) layering. Layers are listed from most abstract to most business-specific. **Higher layers may import from lower layers, never the reverse.**

```
app/
├── pages/          # Nuxt routing — thin page shells, compose from widgets/features
├── layouts/        # Nuxt layouts — compose from widgets
├── middleware/     # Nuxt route guards
├── plugins/        # Nuxt plugins (HTTP client init)
├── assets/         # Global styles
│
├── widgets/        # Compound UI blocks (combine features + entities)
├── features/       # User-facing feature slices
└── shared/         # Reusable code — zero business logic
```

### Layer responsibilities

| Layer | Contains | May import from |
|-------|----------|-----------------|
| `pages/` | Route entry points | `widgets`, `features`, `shared` |
| `layouts/` | App shell templates | `widgets`, `shared` |
| `widgets/` | Composite UI blocks | `features`, `entities`, `shared` |
| `features/` | Business interactions | `entities`, `shared` |
| `entities/` | Business entities | `shared` |
| `shared/` | Infrastructure, utilities | nothing project-internal |

### Naming convention

All files use **kebab-case**: `auth-store.ts`, `use-api-fetch.ts`, `safe-cookie.ts`, `sidebar-nav.vue`.
Functions and exports remain camelCase per JavaScript convention.

---

## Development

```bash
pnpm install
pnpm dev
pnpm typecheck
pnpm lint
pnpm lint:fix
pnpm build
```

### Style & lint

- **ESLint** — flat config in [eslint.config.mjs](eslint.config.mjs). Vue + TypeScript rules, Prettier runs last to resolve formatting conflicts.
- **Prettier** — config in [.prettierrc](.prettierrc): 100-char lines, single quotes, trailing commas `es5`.
- **TypeScript strictness** is delegated to Nuxt-generated `tsconfig.json`. Do not hand-roll a replacement.

Before committing:

```bash
pnpm lint:fix
pnpm nuxt prepare
pnpm typecheck
```

### TypeScript / Vue patterns

- **`<script setup lang="ts">` only.** No Options API. No `defineComponent` wrappers.
- **Typed API fetching** via the generic `useApiFetch<Path, Method>` composable from [app/shared/api/use-api-fetch.ts](app/shared/api/use-api-fetch.ts). Do not call `$fetch` raw in components.
- **Pinia stores** use `defineStore('namespace/name', () => { ... })` setup syntax.
- **i18n keys** live in [i18n/locales/en.json](i18n/locales/en.json) and [i18n/locales/ru.json](i18n/locales/ru.json). Never hardcode user-facing strings in `.vue` templates.

### Auto-imports

Nuxt auto-imports composables, utilities, stores, and widgets from the configured directories. Do not add explicit imports for items already covered by Nuxt auto-imports.

---

## Testing

### Unit tests (Vitest)

```bash
pnpm nuxt prepare
pnpm test
```

### E2E tests (Playwright)

Requires a running application:

```bash
docker compose up -d
pnpm test:e2e:install
pnpm test:e2e
pnpm test:e2e:ui
```

### E2E expectations (gate requirement)

The `/phase-gate` workflow requires a ✅ e2e row before commit — unit tests alone do not clear the gate.

- One spec per user-facing flow introduced in the phase.
- Run against the full Docker stack.
- Chromium is the canonical E2E browser for this template.
- Reporter config should emit `list`, `html`, and `junit`.

---

## Mandatory rules (duplicated locally — these are load-bearing)

Repeated here because an AI editing inside [app/](app/) often will not open the root [../AGENTS.md](../AGENTS.md) first.

1. **Use up-to-date docs before writing code against any external library** — Nuxt, Vue, Pinia, Tailwind, Nuxt UI, Vitest, Playwright, `@nuxtjs/i18n`, or any third-party package. Prefer a configured docs MCP such as Context7 when available, then `ctx7` CLI, then official docs. Full rule in [../AGENTS.md](../AGENTS.md#library-documentation-lookup).

2. **On `EACCES` / `EPERM` / "Permission denied"** — stop immediately, hand off the issue to the user, and follow the recovery guidance in [../docs/KNOWN_GOTCHAS.md](../docs/KNOWN_GOTCHAS.md#docker-owned-files-and-permission-denied-errors). Never `sudo`, `chmod`, or loop.

---

## Regenerating API types

```bash
pnpm generate:api
```

This overwrites `app/shared/types/schema.ts` from the backend OpenAPI spec. Do not edit that file manually.
