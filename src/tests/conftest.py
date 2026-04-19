# conftest.py
import asyncio
from functools import lru_cache

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.settings import settings
from app.db.engine import form_db_url
from app.main import app
from app.models.base import BaseModel
from app.models.refresh import RefreshSession

async_engine = create_async_engine(
    url=form_db_url(),
    echo=True
)

# drop all database every time when test complete
@pytest_asyncio.fixture(scope='session')
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield async_engine

@pytest_asyncio.fixture(scope='session')
async def async_session(async_db_engine):
    yield sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

# truncate all table to isolate tests
@pytest_asyncio.fixture(scope='session')
async def async_db(async_session):
    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()

@pytest_asyncio.fixture(scope='session')
async def async_client(async_db):
    transport = ASGITransport(app=app)

    yield AsyncClient(
        transport=transport,
        base_url="http://localhost/api/v1"
    )

    statement = delete(RefreshSession)
    await async_db.exec(statement)
    await async_db.commit()

# let test session to know it is running inside event loop
@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope='session')
async def admin_access_token(async_client: AsyncClient):
    resp = await async_client.post(
        url='/auth/login',
        data={
            'username': 'admin',
            'password': settings.rbac.admin_password,
        }
    )
    data = resp.json()
    yield data.get("access_token")
