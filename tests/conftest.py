import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

# Use PostgreSQL from CI environment if DATABASE_URL is set,
# otherwise fall back to in-memory SQLite for local unit-level tests.
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///:memory:",
)

# SQLite doesn't support PostgreSQL's JSONB — patch its DDL compiler to use JSON instead.
# This only affects test infrastructure; production uses PostgreSQL.
if TEST_DATABASE_URL.startswith("sqlite"):
    from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

    if not hasattr(SQLiteTypeCompiler, "visit_JSONB"):

        def _visit_JSONB(self, type_, **kw):  # noqa: N802
            return "JSON"

        SQLiteTypeCompiler.visit_JSONB = _visit_JSONB  # type: ignore[attr-defined]

os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only")

import app.db.models  # noqa: F401, E402
from app.core.auth import create_access_token, hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.models.doctor_profile import DoctorProfile  # noqa: E402
from app.db.models.patient_profile import OnboardingStatus, PatientProfile  # noqa: E402
from app.db.models.user import User, UserRole  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
async def test_engine():
    # Async session-scoped fixture so the engine is created and used entirely
    # within pytest-asyncio's session event loop — no loop boundary crossings.
    #
    # PostgreSQL — NullPool prevents asyncpg from caching connections across
    # tests; each db_session opens a fresh connection in the current loop.
    #
    # SQLite — StaticPool shares one in-memory DB across all connections.
    # aiosqlite is thread-based and has no event-loop affinity.
    if TEST_DATABASE_URL.startswith("sqlite"):
        engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def db_session(test_engine) -> AsyncSession:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db() -> AsyncSession:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture()
async def doctor_user(db_session: AsyncSession) -> User:
    user = User(
        email=f"doctor_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("changeme123"),
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(DoctorProfile(user_id=user.id))
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
def doctor_headers(doctor_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(doctor_user.id), "role": doctor_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def other_doctor_user(db_session: AsyncSession) -> User:
    user = User(
        email=f"doctor_other_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("changeme123"),
        role=UserRole.doctor,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(DoctorProfile(user_id=user.id))
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
async def patient_user(db_session: AsyncSession, doctor_user: User) -> User:
    user = User(
        email=f"patient_{uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("temporary123"),
        role=UserRole.patient,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(
        PatientProfile(
            user_id=user.id,
            doctor_user_id=doctor_user.id,
            onboarding_status=OnboardingStatus.pending.value,
            must_change_password=True,
            is_active_with_doctor=True,
        )
    )
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture()
def patient_headers(patient_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(patient_user.id), "role": patient_user.role.value})
    return {"Authorization": f"Bearer {token}"}
