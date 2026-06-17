from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings


def create_engine(settings: Settings):
    return create_async_engine(settings.database_url, pool_pre_ping=True)


def create_sessionmaker(settings: Settings) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(create_engine(settings), expire_on_commit=False)


_sessionmaker = None

def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        from app.config import get_settings
        _sessionmaker = create_sessionmaker(get_settings())
    return _sessionmaker


async def get_session() -> AsyncIterator[AsyncSession]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session

