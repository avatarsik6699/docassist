# Frontend

React 19 + React Router framework mode with server-side rendering, organized as Feature-Sliced Design (FSD).

## Layout

```text
frontend/
├── app/
│   ├── root.tsx              # RR7 root layout
│   ├── routes.ts             # RR7 route registry (do not edit)
│   ├── routes/               # Thin stubs: meta() export + delegate to pages/
│   │   ├── home.tsx
│   │   ├── login.tsx
│   │   └── dashboard.tsx
│   ├── pages/                # FSD: full page compositions
│   │   ├── home/ui/
│   │   ├── login/ui/
│   │   └── dashboard/ui/
│   ├── widgets/              # FSD: composite UI blocks
│   ├── features/             # FSD: feature slices
│   │   └── auth/model/
│   ├── entities/             # FSD: business entities
│   │   └── user/model/
│   ├── shared/               # FSD: utilities, API, types, UI atoms
│   │   ├── api/
│   │   ├── lib/
│   │   ├── types/
│   │   └── ui/
│   └── styles/app.css
├── public/
├── scripts/
├── tests/
│   ├── home.test.tsx
│   └── e2e/home.spec.ts
├── react-router.config.ts    # do not edit
├── vite.config.ts
└── playwright.config.ts
```

## Commands

```bash
pnpm install
pnpm dev
pnpm typecheck
pnpm test
pnpm test:e2e:lint
pnpm test:e2e --project=chromium
pnpm playwright:cli -- open http://localhost:3000 --headed
cd ..
./scripts/install-caveman.sh
pnpm build
pnpm start
```

## Conventions

- Route modules under `app/routes/` are thin stubs. They export `meta()` (required for SSR/SEO) and a default component that delegates rendering to `app/pages/`.
- Never put business logic or heavy JSX in route modules.
- FSD import rule — each layer may only import from layers below it:
  `routes → pages → widgets → features → entities → shared`
- Use path aliases for cross-layer imports: `@pages/`, `@widgets/`, `@features/`, `@entities/`, `@shared/`.
- Relative imports are acceptable within a single slice (e.g., inside `features/auth/`).
- No barrel `index.ts` files are required — import directly from the file (`@pages/home/ui/home-page`).
- `app/routes.ts` and `react-router.config.ts` must never be edited as part of FSD work.
- SSR-safe rendering only in `routes/` stubs and `root.tsx`.
- Global styles stay in `app/styles/app.css`.
- Use Playwright CLI only for explicit manual debugging requests; keep gate automation on deterministic Playwright test commands.
- Use Caveman only as an explicit opt-in response compression mode (`./scripts/install-caveman.sh` + `/caveman` or `$caveman`), not as default project policy.
