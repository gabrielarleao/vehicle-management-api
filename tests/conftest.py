import pytest
import pytest_asyncio
import asyncio
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base, AuthBase, get_db, get_auth_db
from app.main import app


# Criar engines de teste em memória
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_AUTH_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_auth_engine = create_async_engine(TEST_AUTH_DATABASE_URL, echo=False)

TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
TestAuthSessionLocal = async_sessionmaker(test_auth_engine, class_=AsyncSession, expire_on_commit=False)


# Mock simples para bcrypt nos testes
def mock_hash(password: str) -> str:
    return f"hashed_{password}"

def mock_verify(plain_password: str, hashed_password: str) -> bool:
    return f"hashed_{plain_password}" == hashed_password


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Cria uma sessão de banco de dados para testes"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def auth_db_session():
    """Cria uma sessão de banco de dados de autenticação para testes"""
    async with test_auth_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)
    
    async with TestAuthSessionLocal() as session:
        yield session
    
    async with test_auth_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def override_dependencies(db_session, auth_db_session):
    """Sobrescreve as dependências do FastAPI para usar os bancos de teste"""
    async def override_get_db():
        yield db_session
    
    async def override_get_auth_db():
        yield auth_db_session
    
    # Mock das funções de hash para evitar problema com bcrypt
    with patch('app.core.security.get_password_hash', side_effect=mock_hash), \
         patch('app.core.security.verify_password', side_effect=mock_verify), \
         patch('app.services.user_service.get_password_hash', side_effect=mock_hash), \
         patch('app.services.user_service.verify_password', side_effect=mock_verify):
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_auth_db] = override_get_auth_db
        
        yield
        
        app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para toda a sessão de testes"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
