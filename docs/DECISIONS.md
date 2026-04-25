# Decisions

> Template memory file for derived projects.
> Record only important technical decisions that future agents or humans are likely to revisit.

## How To Use

- Add a new entry when you make a meaningful architectural or workflow decision.
- Keep each entry brief: context, decision, consequence.
- Link to the relevant PR, issue, phase, or spec section when available.

## Decision Log

### 2026-04-25 — Backend layout: modular DDD with bounded contexts

- Context: The starter layout (`app/api/v1/`, `app/services/`, `app/schemas/`, `app/db/models/`) is layered. With a new domain (`User`/`Auth`) already showing the strain — duplicated `Role` enum, business logic in route handlers, no service or repository layer — keeping the layered shape would lock that pattern in for every future domain.
- Decision: Restructure the backend into bounded-context modules under `app/modules/<name>/`. Each module owns the full vertical slice (`api.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, `dependencies.py`, `exceptions.py`, `constants.py`, `config.py`, `utils.py`) and exposes its public surface via the package's `__init__.py`. Cross-module imports go only through the package root; cross-module DB joins are forbidden — modules talk via injected services. Common framework infrastructure stays in `app/core/`; domain-agnostic reusables in `app/shared/`.
- Auth and Users are split: `users` owns the `User` table and profile/role concerns, `auth` owns JWT, login flow, and `get_current_user` / `require_role`. `auth → users` is the only allowed direction.
- Module boundaries are enforced by convention and code review — no `import-linter` yet (deferred until repeated violations appear or the team grows).
- Consequences: New domains scale horizontally with a stable per-module layout; route handlers stay thin; the same domain's tests, ORM, and DTOs sit next to each other. Adds slight upfront ceremony (multiple files per module) — accepted because the pattern is now load-bearing for every future feature.
- Links: `docs/SPEC.md` §4.1, `app/README.md`, `app/modules/`, `docs/CHANGELOG.md` v1.1.

### 2026-04-24 — Frontend UI Baseline (shadcn + i18n + themes)

- Context: The project intentionally avoids a client-side state manager at startup and focuses on server state with React Query, while needing a concrete UI baseline for components, themes, and internationalization.
- Decision: Standardize frontend UI on `shadcn/ui` (Radix base) + Tailwind CSS v4, `next-themes` for dark/system theme, and `i18next` + `react-i18next` for localization. Keep `@tanstack/react-query` as the only state/data orchestration layer for remote data.
- Consequences: UI primitives are local source files and can be customized without vendor lock-in; theming and i18n are available from phase 1; no Redux/Zustand/Pinia-like store is introduced in the current baseline.
- Links: `docs/STACK.md`, `docs/SPEC.md` section 5, `frontend/components.json`, `docs/PHASE_01.md`
