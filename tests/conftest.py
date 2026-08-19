import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from auth.dependencies import get_current_user
from db.models import User
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

    main_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def create_team(client):
    async def _create_team(
        name: str = "Backend",
        description: str = "Backend team",
    ):
        response = await client.post(
            "api/team/", json={"name": name, "description": description}
        )

        assert response.status_code == 200, response.json()
        return response.json()

    return _create_team


@pytest_asyncio.fixture
async def authenticated_user(session):
    user = User(
        email="test@test.com",
        username="testuser",
        hashed_password="fakehash",
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    async def override_get_current_user():
        return user

    main_app.dependency_overrides[get_current_user] = override_get_current_user

    yield user

    main_app.dependency_overrides.pop(get_current_user, None)
