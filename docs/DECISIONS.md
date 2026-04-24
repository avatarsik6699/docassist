# Decisions

> Template memory file for derived projects.
> Record only important technical decisions that future agents or humans are likely to revisit.

## How To Use

- Add a new entry when you make a meaningful architectural or workflow decision.
- Keep each entry brief: context, decision, consequence.
- Link to the relevant PR, issue, phase, or spec section when available.

## Decision Log

### 2026-04-24 — Frontend UI Baseline (shadcn + i18n + themes)

- Context: The project intentionally avoids a client-side state manager at startup and focuses on server state with React Query, while needing a concrete UI baseline for components, themes, and internationalization.
- Decision: Standardize frontend UI on `shadcn/ui` (Radix base) + Tailwind CSS v4, `next-themes` for dark/system theme, and `i18next` + `react-i18next` for localization. Keep `@tanstack/react-query` as the only state/data orchestration layer for remote data.
- Consequences: UI primitives are local source files and can be customized without vendor lock-in; theming and i18n are available from phase 1; no Redux/Zustand/Pinia-like store is introduced in the current baseline.
- Links: `docs/STACK.md`, `docs/SPEC.md` section 5, `frontend/components.json`, `docs/PHASE_01.md`
