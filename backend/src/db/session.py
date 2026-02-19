from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.config import settings


# 1. Создаем движок (Engine)
engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
    future=True
)

# 2. Создаем фабрику сессий
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# 3. Dependency для FastAPI
async def get_async_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

            