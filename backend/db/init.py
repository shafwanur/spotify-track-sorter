from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import Base

engine = create_async_engine("postgresql+asyncpg://postgres:postgres@db:5432/spotify", echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# db/session.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Success: DB initialized.")
