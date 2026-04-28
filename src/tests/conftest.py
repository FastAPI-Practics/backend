
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.engine import form_test_db_url
from app.dependencies.session import get_session
from app.main import app
from app.models.refresh import RefreshSession
from app.core.settings import settings
from app.models.roles import Role
from app.utils.hasher import Hasher
from app.models.users import UserModel, UserStatus


@pytest_asyncio.fixture(scope='session')
async def async_db_engine():
    async_engine = create_async_engine(
        form_test_db_url()
    )
    yield async_engine


@pytest_asyncio.fixture(scope='session')
async def async_session(async_db_engine):
    yield sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession
    )

@pytest_asyncio.fixture(scope='session')
async def async_db(async_session):
    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()

@pytest_asyncio.fixture(scope='session')
async def async_client(async_db):
    transport = ASGITransport(app=app)

    async def get_session_override():
        yield async_db

    app.dependency_overrides[get_session] = get_session_override

    yield AsyncClient(
        transport=transport,
        base_url="http://localhost/api/v1"
    )

    statement = delete(RefreshSession)
    await async_db.exec(statement)
    await async_db.commit()

@pytest_asyncio.fixture(scope='session')
async def admin_access_token(async_client: AsyncClient):
    resp = await async_client.post(
        url="/auth/login",
        data={
            'username': 'admin',
            'password': settings.rbac.admin_password
        }
    )
    data = resp.json()
    yield data.get('access_token')

@pytest_asyncio.fixture(scope='session')
async def public_access_token(
    async_db: AsyncSession,
    async_client: AsyncClient
):
    public_role_stmt = select(Role).where(Role.name == settings.rbac.public_role)
    public_role = (await async_db.scalars(public_role_stmt)).first()

    password = "pass"
    password_hash = Hasher.get_password_hash(password)

    user = UserModel(
        first_name="first_name",
        last_name="last_name",
        username="public-user",
        email="email@gmail.com",
        status=UserStatus.CONFIRMED,
        password_hash=password_hash
    )

    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)

    user.role = public_role
    await async_db.commit()
    await async_db.refresh(user)

    resp = await async_client.post(
        url="/auth/login",
        data={
            'username': user.username,
            'password': password
        }
    )
    data = resp.json()
    yield data.get('access_token')

    await async_db.delete(user)
    await async_db.commit()
