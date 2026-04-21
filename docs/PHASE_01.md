# PHASE 01 — Foundation, auth, user roles, project skeleton

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. Be concise. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `01` |
| Title | Foundation, auth, user roles, project skeleton |
| Status | `✅ done` |
| Tag | `v0.1.0` |
| Depends on | None (first phase) |
| CONTEXT.md version | `v1.2` |

---

## Phase Goal

This phase establishes the MVP foundation required by the product constraints in `docs/SPEC.md`: secure login, server-side authorization boundaries, and a usable project skeleton that works on desktop and mobile web. It should leave the repository in a state where `admin`, `doctor`, and `patient` users can be represented safely, authentication works end-to-end, and later phases can add doctor-patient relationships, medication tracking, and questionnaires without reworking the stack basics.

---

## Scope

### Backend
- [ ] Create the FastAPI foundation: app wiring, settings, async DB session, health check, and versioned API routing
- [ ] Add the initial user/auth data model with role support for `admin`, `doctor`, and `patient`
- [ ] Implement JWT-based login, current-user lookup, and logout stub endpoints with server-side auth enforcement
- [ ] Add the first Alembic migration and seed a default admin account for initial access

### Frontend
- [ ] Create the Nuxt application skeleton with shared layouts, route middleware, and typed API plumbing
- [ ] Build the login flow and an authenticated dashboard shell for post-login navigation
- [ ] Add client-side auth state management that persists JWT state safely across page loads

---

## Files

### Create / modify
~~~
.env.example
alembic/env.py
alembic/versions/0001_users_table.py
app/api/v1/auth.py
app/api/v1/health.py
app/core/auth.py
app/core/config.py
app/db/base.py
app/db/models/user.py
app/db/session.py
app/main.py
app/schemas/auth.py
docker-compose.yml
frontend/app/app.vue
frontend/app/assets/css/main.css
frontend/app/features/auth/model/auth-store.ts
frontend/app/layouts/blank.vue
frontend/app/layouts/default.vue
frontend/app/middleware/auth.global.ts
frontend/app/pages/dashboard.vue
frontend/app/pages/index.vue
frontend/app/pages/login.vue
frontend/app/plugins/api.ts
frontend/app/shared/api/use-api-fetch.ts
frontend/app/shared/lib/safe-cookie.ts
frontend/tests/ui-store.test.ts
tests/conftest.py
tests/test_auth_api.py
tests/test_health.py
~~~

### Do NOT touch
- `docs/SPEC.md`
- `docs/CONTEXT.md`
- `docs/SPEC_POST_MVP.md`
- Product-scope files for later phases such as questionnaire, medication, side-effect, and patient-summary features

---

## Contracts

> This section is the source of truth for `/context-update`. Fill it in **before** handing to AI.

### New DB tables / columns
~~~
users(
  id UUID PK,
  email TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  role ENUM['admin','doctor','patient'] NOT NULL,
  is_active BOOLEAN NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
~~~

### New API endpoints
| Method | Path | Auth | Response |
|--------|------|------|----------|
| `GET` | `/api/v1/health` | none | `{"status":"ok"}` |
| `POST` | `/api/v1/auth/login` | none | `{"access_token": "string", "token_type": "bearer"}` |
| `GET` | `/api/v1/auth/me` | JWT | `{"id":"uuid","email":"user@example.com","role":"admin|doctor|patient","is_active":true}` |
| `POST` | `/api/v1/auth/logout` | JWT | `{"message":"logged out"}` |

### New TypeScript types / Pinia stores
```typescript
type AuthUser = {
  id: string
  email: string
  role: 'admin' | 'doctor' | 'patient'
  is_active: boolean
}

// useAuthStore — tracks JWT session state, current user bootstrap, login/logout actions,
// and redirect behavior for authenticated routes
```

### New env vars (add to `.env.example`)
| Key | Example value | Required |
|-----|---------------|----------|
| `DATABASE_URL` | `postgresql+asyncpg://app_user:changeme@db:5432/docassist` | yes |
| `POSTGRES_USER` | `app_user` | yes |
| `POSTGRES_PASSWORD` | `changeme` | yes |
| `POSTGRES_DB` | `docassist` | yes |
| `REDIS_URL` | `redis://redis:6379/0` | yes |
| `SECRET_KEY` | `change-me-to-a-long-random-secret` | yes |
| `ALGORITHM` | `HS256` | yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | yes |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost` | yes |
| `APP_ENV` | `development` | yes |
| `LOG_LEVEL` | `INFO` | yes |
| `API_BASE_URL` | `http://localhost:8000/api/v1` | yes |

---

## Gate Checks

Run `/phase-gate 01` before committing.

`/phase-gate` returns full PASS only when:
- Automated checks are green
- All architect review items below are resolved (checked off)

Use the standard infrastructure, migration, test, prep, typecheck, unit, and e2e commands from [docs/STACK.md](./STACK.md#gate-commands).

Phase-specific smoke override:

```bash
curl -s http://localhost:8000/api/v1/health
# expected: {"status":"ok"}

./scripts/phase-gate.sh 01
```

---

## Architect Review Notes

Use this section after manual verification. Add one checkbox item per issue the architect wants fixed before the phase can close.
Leave the item unchecked while it is still open. Check it off only after the fix is implemented and re-verified.
If manual verification found nothing, keep the default checked line below.

- [x] When I log in for the first time, enter my email and password, and then click Sign in, nothing happens after that. When I click Sign in again, it's only the second time that I go to the main page "/dashboard". We need to fix this behavior - the transition to the page / dashboard should occur immediately, after correctly entering the email and password and after the first click on the Sign in button.
- [x] I think it's worth refining the e2e tests and covering all the basic scenarios. Right now, e2e tests are not doing any useful work. This includes testing the flow of logging in and logging out.

---

## Atomic Commit Message

```text
feat(phase-01): foundation auth roles and project skeleton
```

---

## Post-Phase Checklist

- [x] All automated gate checks green
- [x] All architect review notes resolved
- [x] `docs/CONTEXT.md` updated — run `/context-update 01`
- [x] `docs/STATE.md` phase row updated to `✅ done`
- [x] `docs/CHANGELOG.md` entry added (if CONTEXT.md version bumped)
- [ ] Committed atomically on `feat/phase-01` branch
- [ ] Tag created after merge to develop: `git tag -a v0.1.0 -m "Phase 01: Foundation, auth, user roles, project skeleton"`
