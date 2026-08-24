import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from auth.dependencies import get_current_user
from db.models import User
from db.models.user import UserRole
from main import main_app
from db import db_helper
from db.base import Base

TEST_DB_URL = "postgresql+asyncpg://user:password@localhost:5433/smartrepbase_tests"


@pytest_asyncio.fixture
async def engine():
    test_engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def prepare_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(engine):

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_session():
        async with async_session() as session:
            yield session

    main_app.dependency_overrides[db_helper.session_getter] = override_session

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    main_app.dependency_overrides.pop(db_helper.session_getter, None)


@pytest_asyncio.fixture
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as s:
        yield s


async def _create_user(
    session: AsyncSession,
    role: UserRole,
    email: str,
    username: str,
):
    user = User(
        email=email,
        username=username,
        hashed_password="fakehash",
        role=role,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def admin_user(session):
    return await _create_user(
        session,
        UserRole.ADMIN,
        "admin@test.com",
        "admin",
    )


@pytest_asyncio.fixture
async def team_lead_user(session):
    return await _create_user(
        session,
        UserRole.TEAM_LEAD,
        "lead@test.com",
        "lead",
    )


@pytest_asyncio.fixture
async def worker_user(session):
    return await _create_user(
        session,
        UserRole.WORKER,
        "worker@test.com",
        "worker",
    )


@pytest_asyncio.fixture
async def second_worker_user(session):
    return await _create_user(
        session,
        UserRole.WORKER,
        "secondworker@test.com",
        "second_worker",
    )


class AuthenticatedClient:
    def __init__(self, client: AsyncClient, user: User):
        self.client = client
        self.user = user

    def _activate(self):
        async def override_get_current_user():
            return self.user

        main_app.dependency_overrides[get_current_user] = override_get_current_user

    async def get(self, *args, **kwargs):
        self._activate()
        return await self.client.get(*args, **kwargs)

    async def post(self, *args, **kwargs):
        self._activate()
        return await self.client.post(*args, **kwargs)

    async def patch(self, *args, **kwargs):
        self._activate()
        return await self.client.patch(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        self._activate()
        return await self.client.delete(*args, **kwargs)


@pytest_asyncio.fixture
async def admin_client(client, admin_user):
    return AuthenticatedClient(client, admin_user)


@pytest_asyncio.fixture
async def team_lead_client(client, team_lead_user):
    return AuthenticatedClient(client, team_lead_user)


@pytest_asyncio.fixture
async def worker_client(client, worker_user):
    return AuthenticatedClient(client, worker_user)


@pytest_asyncio.fixture
async def create_team(admin_client):
    async def _create_team(
        name: str = "Backend",
        description: str = "Backend team",
    ):
        response = await admin_client.post(
            "/api/team/", json={"name": name, "description": description}
        )

        assert response.status_code == 200, response.json()
        return response.json()

    return _create_team
