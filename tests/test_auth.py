import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_register_user(override_dependencies):
    """Testa registro de novo usuário"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        user_data = {
            "email": "test@example.com",
            "password": "senha123",
            "full_name": "Test User"
        }
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["is_active"] == True


@pytest.mark.asyncio
async def test_register_duplicate_email(override_dependencies):
    """Testa registro com email duplicado"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        user_data = {
            "email": "duplicate@example.com",
            "password": "senha123"
        }
        # Primeiro registro
        await ac.post("/auth/register", json=user_data)
        
        # Segundo registro com mesmo email
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "já cadastrado" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(override_dependencies):
    """Testa registro com email inválido"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        user_data = {
            "email": "invalid-email",
            "password": "senha123"
        }
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(override_dependencies):
    """Testa registro com senha curta"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        user_data = {
            "email": "test@example.com",
            "password": "123"  # Menos de 6 caracteres
        }
        response = await ac.post("/auth/register", json=user_data)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(override_dependencies):
    """Testa login com sucesso"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Registra usuário
        user_data = {
            "email": "login@example.com",
            "password": "senha123"
        }
        await ac.post("/auth/register", json=user_data)
        
        # Faz login
        login_data = {
            "email": "login@example.com",
            "password": "senha123"
        }
        response = await ac.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(override_dependencies):
    """Testa login com senha errada"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Registra usuário
        user_data = {
            "email": "wrongpass@example.com",
            "password": "senha123"
        }
        await ac.post("/auth/register", json=user_data)
        
        # Tenta login com senha errada
        login_data = {
            "email": "wrongpass@example.com",
            "password": "senhaerrada"
        }
        response = await ac.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "inválidas" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(override_dependencies):
    """Testa login com usuário inexistente"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_data = {
            "email": "nonexistent@example.com",
            "password": "senha123"
        }
        response = await ac.post("/auth/login", json=login_data)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(override_dependencies):
    """Testa obter dados do usuário autenticado"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Registra e faz login
        user_data = {
            "email": "me@example.com",
            "password": "senha123",
            "full_name": "Me User"
        }
        await ac.post("/auth/register", json=user_data)
        
        login_response = await ac.post("/auth/login", json={
            "email": "me@example.com",
            "password": "senha123"
        })
        token = login_response.json()["access_token"]
        
        # Busca dados do usuário
        response = await ac.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["full_name"] == "Me User"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(override_dependencies):
    """Testa acesso sem autenticação"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/auth/me")
        assert response.status_code == 403  # Forbidden (no token)


@pytest.mark.asyncio
async def test_get_me_invalid_token(override_dependencies):
    """Testa acesso com token inválido"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
