import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.db.engine import form_db_url
from app.models.base import BaseModel
from init import bootstrap_app

async_engine = create_async_engine(
    url=form_db_url(),
)

async def init():
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        await conn.commit()
        await bootstrap_app()

if __name__ == '__main__':
    asyncio.run(init())