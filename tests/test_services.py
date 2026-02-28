import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base, AuthBase
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.user import User
from app.schemas.schemas import VehicleCreate, VehicleUpdate, UserCreate, UserLogin
from app.services.vehicle_service import VehicleService
from app.services.user_service import UserService


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

TEST_AUTH_DB_URL = "sqlite+aiosqlite:///:memory:"
test_auth_engine = create_async_engine(TEST_AUTH_DB_URL, echo=False)
TestAuthSession = async_sessionmaker(test_auth_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def vehicle_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def auth_db():
    async with test_auth_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)
    async with TestAuthSession() as session:
        yield session
    async with test_auth_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.drop_all)


def mock_hash(password: str) -> str:
    return f"hashed_{password}"


def mock_verify(plain: str, hashed: str) -> bool:
    return f"hashed_{plain}" == hashed


# --- VehicleService ---

@pytest.mark.asyncio
async def test_vehicle_service_create(vehicle_db):
    svc = VehicleService(vehicle_db)
    v = await svc.create_vehicle(VehicleCreate(
        marca="Toyota", modelo="Corolla", ano=2023, cor="Preto", preco=95000.0
    ))
    assert v.id is not None
    assert v.marca == "Toyota"
    assert v.status == VehicleStatus.DISPONIVEL


@pytest.mark.asyncio
async def test_vehicle_service_get_vehicles(vehicle_db):
    svc = VehicleService(vehicle_db)
    await svc.create_vehicle(VehicleCreate(marca="A", modelo="M", ano=2020, cor="X", preco=50000))
    await svc.create_vehicle(VehicleCreate(marca="B", modelo="N", ano=2021, cor="Y", preco=30000))
    vehicles = await svc.get_vehicles()
    assert len(vehicles) == 2
    assert vehicles[0].preco <= vehicles[1].preco


@pytest.mark.asyncio
async def test_vehicle_service_get_vehicles_by_status(vehicle_db):
    svc = VehicleService(vehicle_db)
    await svc.create_vehicle(VehicleCreate(marca="A", modelo="M", ano=2020, cor="X", preco=50000))
    vehicles = await svc.get_vehicles(status=VehicleStatus.DISPONIVEL)
    assert len(vehicles) == 1
    sold = await svc.get_vehicles(status=VehicleStatus.VENDIDO)
    assert len(sold) == 0


@pytest.mark.asyncio
async def test_vehicle_service_get_vehicle(vehicle_db):
    svc = VehicleService(vehicle_db)
    v = await svc.create_vehicle(VehicleCreate(marca="A", modelo="M", ano=2020, cor="X", preco=50000))
    found = await svc.get_vehicle(v.id)
    assert found is not None
    assert found.id == v.id


@pytest.mark.asyncio
async def test_vehicle_service_get_vehicle_not_found(vehicle_db):
    svc = VehicleService(vehicle_db)
    found = await svc.get_vehicle(999)
    assert found is None


@pytest.mark.asyncio
async def test_vehicle_service_update(vehicle_db):
    svc = VehicleService(vehicle_db)
    v = await svc.create_vehicle(VehicleCreate(marca="A", modelo="M", ano=2020, cor="X", preco=50000))
    updated = await svc.update_vehicle(v.id, VehicleUpdate(preco=60000, cor="Azul"))
    assert updated.preco == 60000
    assert updated.cor == "Azul"


@pytest.mark.asyncio
async def test_vehicle_service_update_not_found(vehicle_db):
    svc = VehicleService(vehicle_db)
    result = await svc.update_vehicle(999, VehicleUpdate(preco=60000))
    assert result is None


@pytest.mark.asyncio
async def test_vehicle_service_delete(vehicle_db):
    svc = VehicleService(vehicle_db)
    v = await svc.create_vehicle(VehicleCreate(marca="A", modelo="M", ano=2020, cor="X", preco=50000))
    deleted = await svc.delete_vehicle(v.id)
    assert deleted is True
    assert await svc.get_vehicle(v.id) is None


@pytest.mark.asyncio
async def test_vehicle_service_delete_not_found(vehicle_db):
    svc = VehicleService(vehicle_db)
    deleted = await svc.delete_vehicle(999)
    assert deleted is False


# --- UserService ---

@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_create(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    user = await svc.create_user(UserCreate(
        email="test@test.com", password="senha123", full_name="Test"
    ))
    assert user.email == "test@test.com"
    assert user.hashed_password == "hashed_senha123"


@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_duplicate_email(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    await svc.create_user(UserCreate(email="dup@test.com", password="senha123"))
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(UserCreate(email="dup@test.com", password="senha123"))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_authenticate(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    await svc.create_user(UserCreate(email="auth@test.com", password="senha123"))
    result = await svc.authenticate_user(UserLogin(email="auth@test.com", password="senha123"))
    assert result["access_token"] == "test-token"
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_authenticate_wrong_password(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    await svc.create_user(UserCreate(email="wp@test.com", password="senha123"))
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await svc.authenticate_user(UserLogin(email="wp@test.com", password="wrong"))
    assert exc.value.status_code == 401


@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_authenticate_nonexistent(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await svc.authenticate_user(UserLogin(email="no@test.com", password="senha123"))
    assert exc.value.status_code == 401


@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_get_by_id(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    user = await svc.create_user(UserCreate(email="id@test.com", password="senha123"))
    found = await svc.get_user_by_id(user.id)
    assert found is not None
    assert found.email == "id@test.com"


@pytest.mark.asyncio
@patch('app.services.user_service.get_password_hash', side_effect=mock_hash)
@patch('app.services.user_service.verify_password', side_effect=mock_verify)
@patch('app.services.user_service.create_access_token', return_value="test-token")
async def test_user_service_get_by_id_not_found(mock_token, mock_vp, mock_hp, auth_db):
    svc = UserService(auth_db)
    found = await svc.get_user_by_id(999)
    assert found is None
