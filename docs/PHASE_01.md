# PHASE 01 — Foundation & Core Data

<!-- TOKEN BUDGET: keep this file under 10,000 tokens. -->

## Phase Metadata

| Field | Value |
|-------|-------|
| Phase | `01` |
| Title | Foundation & Core Data |
| Status | `⏳ pending` |
| Tag | `v0.1.0` |
| Depends on | — (first phase) |
| CONTEXT.md version | `v1.0` |

---

## Phase Goal

Stand up the complete foundational infrastructure: Docker services, database with migrations, JWT authentication, and a React Router SSR skeleton with auth routes. This is the bedrock on which all future phases build — nothing can proceed until these gate checks are green.

---

## Scope

### Backend
- [ ] Docker Compose: `db` (postgres), `redis`, `backend`, `frontend`, `nginx` — all healthy
- [ ] Alembic migration `0001_users_table` applied
- [ ] `GET /api/v1/health` → `{"status": "ok", "db": "connected"}`
- [ ] `POST /api/v1/auth/login` → JWT `access_token`
- [ ] `GET /api/v1/auth/me` → current user object
- [ ] Seeded admin: `admin@example.com` / `changeme123`

### Frontend
- [ ] React Router SSR app starts without errors
- [ ] Page `/login` — login form (blank layout)
- [ ] Page `/dashboard` — stub after login (default layout)
- [ ] Auth guard: unauthenticated users redirect to `/login`

### Tests
- [ ] `uv run pytest tests/ -v` — all pass
- [ ] `cd frontend && pnpm vitest run` — all pass
- [ ] `cd frontend && pnpm exec tsc --noEmit` — 0 errors

---

## Files

### Create / modify
~~~
app/
├── main.py                # FastAPI app + CORS + X-Request-ID middleware
├── core/config.py         # Pydantic Settings
├── core/auth.py           # JWT + bcrypt + RBAC
├── db/base.py             # Base + UUID/Timestamp mixins
├── db/session.py          # async_sessionmaker + get_db()
├── db/models/user.py      # User model
├── api/v1/health.py       # GET /health
├── api/v1/auth.py         # POST /login, GET /me, POST /logout
└── schemas/auth.py        # LoginRequest, TokenResponse, UserOut
alembic/versions/0001_users_table.py
frontend/app/
├── root.tsx
├── routes.ts
└── routes/
    ├── home.tsx
    ├── login.tsx
    └── dashboard.tsx
tests/
├── conftest.py
├── test_health.py
└── test_auth_api.py
~~~

### Do NOT touch
- Everything else — implemented in subsequent phases

---

## Contracts

> This section is the source of truth for `/context-update 01`.

### New DB tables / columns
~~~
users(
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR     UNIQUE NOT NULL,
  hashed_password VARCHAR   NOT NULL,
  role          userrole    NOT NULL DEFAULT 'admin',
  is_active     BOOLEAN     NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
)
~~~

### New API endpoints
| Method | Path | Auth | Response |
|--------|------|------|----------|
| `GET`  | `/api/v1/health` | — | `{"status": "ok", "db": "connected"}` |
| `POST` | `/api/v1/auth/login` | — | `{"access_token": "...", "token_type": "bearer"}` |
| `GET`  | `/api/v1/auth/me` | JWT | `{"id": "...", "email": "...", "role": "..."}` |
| `POST` | `/api/v1/auth/logout` | JWT | `{"message": "Logged out"}` |

### New TypeScript types / Pinia stores
```typescript
// LoginRequest
{ email: string; password: string }

// TokenResponse
{ access_token: string; token_type: string }

// UserOut
{ id: string; email: string; role: string; is_active: boolean }

// Pinia: useAuthStore — login(), fetchMe(), logout(), token, user, isAuthenticated
// Pinia: useUiStore   — UI state (sidebar, loading, etc.)
```

### New env vars (add to `.env.example`)
| Key | Example value | Required |
|-----|---------------|----------|
| `DATABASE_URL` | `postgresql+asyncpg://app_user:changeme@localhost:5432/docassist` | yes |
| `POSTGRES_USER` | `app_user` | yes |
| `POSTGRES_PASSWORD` | `changeme` | yes |
| `POSTGRES_DB` | `docassist` | yes |
| `REDIS_URL` | `redis://localhost:6379/0` | yes |
| `SECRET_KEY` | `<generate: python -c "import secrets; print(secrets.token_hex(32))">` | yes |
| `ALGORITHM` | `HS256` | yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | yes |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | yes |
| `APP_ENV` | `development` | yes |
| `LOG_LEVEL` | `INFO` | yes |
| `API_BASE_URL` | `http://localhost:8000` | yes |

---

## Gate Checks

All must be green before committing. Run with `/phase-gate 01`.

```bash
# 1. Infrastructure
docker compose up -d db redis
docker compose ps  # db + redis must show: healthy

# 2. Migrations
DATABASE_URL=postgresql+asyncpg://app_user:changeme@localhost:5432/docassist \
  uv run alembic upgrade head

# 3. Backend tests
uv run pytest tests/ -v

# 4. Health check smoke test
curl -s http://localhost:8000/api/v1/health
# expected: {"status":"ok","db":"connected"}

# 5. Frontend
cd frontend
pnpm install --frozen-lockfile
pnpm typecheck
pnpm test
```

---

## Atomic Commit Message

```
feat(phase-01): foundation — docker, db, jwt auth, react-router skeleton
```

---

## Post-Phase Checklist

- [ ] All gate checks green (run `/phase-gate 01`)
- [ ] `docs/CONTEXT.md` updated — run `/context-update 01`
- [ ] `docs/STATE.md` PHASE_01 row updated to `✅ done`
- [ ] `docs/CHANGELOG.md` entry added (CONTEXT.md will bump to `v1.1`)
- [ ] Committed atomically on `feat/phase-01` branch
- [ ] Tag created after merge to develop: `git tag -a v0.1.0 -m "Phase 01: Foundation & Core Data"`
