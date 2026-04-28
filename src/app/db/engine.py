from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.settings import settings

def form_test_db_url() -> str:
    return URL.create(
        drivername="sqlite+aiosqlite",
        database="db.sqlite3",
    ).render_as_string(hide_password=False)


def form_db_url() -> str:
    return URL.create(
        drivername=settings.db.driver,
        username=settings.db.user,
        password=settings.db.password,
        host=settings.db.host,
        port=settings.db.port,
        database=settings.db.name,
    ).render_as_string(hide_password=False)


engine = create_async_engine(
    url=form_db_url(),
    pool_size=10,  # Keep 10 connections
    max_overflow=20,  # Allow 20 extra
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600,  # Recycle after 1 hour
)
