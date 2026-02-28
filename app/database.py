from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Engine para banco transacional (Vehicles)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Engine SEPARADO para banco de autenticação (Users)
auth_engine = create_async_engine(
    settings.AUTH_DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

AuthAsyncSessionLocal = sessionmaker(
    auth_engine, class_=AsyncSession, expire_on_commit=False
)

AuthBase = declarative_base()


async def get_db():
    """Dependency para banco de dados transacional (veículos)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_auth_db():
    """Dependency para banco de dados de autenticação (SEPARADO)"""
    async with AuthAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
