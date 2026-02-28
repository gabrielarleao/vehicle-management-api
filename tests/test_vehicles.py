import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_vehicle(override_dependencies):
    """Testa a criação de um veículo"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        vehicle_data = {
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Preto",
            "preco": 95000.00
        }
        response = await ac.post("/api/v1/vehicles/", json=vehicle_data)
        assert response.status_code == 201
        data = response.json()
        assert data["marca"] == "Toyota"
        assert data["modelo"] == "Corolla"
        assert data["ano"] == 2023
        assert data["status"] == "DISPONIVEL"


@pytest.mark.asyncio
async def test_create_vehicle_invalid_price(override_dependencies):
    """Testa criação de veículo com preço inválido"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        vehicle_data = {
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Preto",
            "preco": -1000  # Preço negativo
        }
        response = await ac.post("/api/v1/vehicles/", json=vehicle_data)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_vehicles_empty(override_dependencies):
    """Testa listagem de veículos quando vazia"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/vehicles/")
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_list_vehicles_ordered_by_price(override_dependencies):
    """Testa que veículos são ordenados por preço"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cria veículos com preços diferentes
        vehicles = [
            {"marca": "Ford", "modelo": "Focus", "ano": 2021, "cor": "Azul", "preco": 150000.00},
            {"marca": "Chevrolet", "modelo": "Onix", "ano": 2022, "cor": "Prata", "preco": 70000.00},
            {"marca": "Honda", "modelo": "Civic", "ano": 2020, "cor": "Branco", "preco": 120000.00},
        ]
        
        for v in vehicles:
            await ac.post("/api/v1/vehicles/", json=v)
        
        # Lista e verifica ordenação
        response = await ac.get("/api/v1/vehicles/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Verifica ordem crescente de preço
        assert data[0]["preco"] == 70000.00
        assert data[1]["preco"] == 120000.00
        assert data[2]["preco"] == 150000.00


@pytest.mark.asyncio
async def test_list_vehicles_by_status(override_dependencies):
    """Testa listagem filtrada por status"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cria veículo
        vehicle_data = {
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Preto",
            "preco": 95000.00
        }
        await ac.post("/api/v1/vehicles/", json=vehicle_data)
        
        # Filtra por DISPONIVEL
        response = await ac.get("/api/v1/vehicles/?status=DISPONIVEL")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        # Filtra por VENDIDO
        response = await ac.get("/api/v1/vehicles/?status=VENDIDO")
        assert response.status_code == 200
        assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_vehicle(override_dependencies):
    """Testa a busca de um veículo específico"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Criar um veículo primeiro
        vehicle_data = {
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2022,
            "cor": "Branco",
            "preco": 85000.00
        }
        create_response = await ac.post("/api/v1/vehicles/", json=vehicle_data)
        vehicle_id = create_response.json()["id"]
        
        # Buscar o veículo
        response = await ac.get(f"/api/v1/vehicles/{vehicle_id}")
        assert response.status_code == 200
        assert response.json()["id"] == vehicle_id
        assert response.json()["marca"] == "Honda"


@pytest.mark.asyncio
async def test_get_vehicle_not_found(override_dependencies):
    """Testa busca de veículo inexistente"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/vehicles/999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_vehicle(override_dependencies):
    """Testa a atualização de um veículo"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Criar um veículo primeiro
        vehicle_data = {
            "marca": "Ford",
            "modelo": "Focus",
            "ano": 2021,
            "cor": "Azul",
            "preco": 70000.00
        }
        create_response = await ac.post("/api/v1/vehicles/", json=vehicle_data)
        vehicle_id = create_response.json()["id"]
        
        # Atualizar o veículo
        update_data = {"preco": 75000.00, "cor": "Verde"}
        response = await ac.put(f"/api/v1/vehicles/{vehicle_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["preco"] == 75000.00
        assert response.json()["cor"] == "Verde"


@pytest.mark.asyncio
async def test_update_vehicle_status(override_dependencies):
    """Testa atualização de status do veículo"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Criar veículo
        vehicle_data = {
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "cor": "Preto",
            "preco": 95000.00
        }
        create_response = await ac.post("/api/v1/vehicles/", json=vehicle_data)
        vehicle_id = create_response.json()["id"]
        
        # Atualizar status para VENDIDO
        update_data = {"status": "VENDIDO"}
        response = await ac.put(f"/api/v1/vehicles/{vehicle_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["status"] == "VENDIDO"


@pytest.mark.asyncio
async def test_update_vehicle_not_found(override_dependencies):
    """Testa atualização de veículo inexistente"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        update_data = {"preco": 75000.00}
        response = await ac.put("/api/v1/vehicles/999", json=update_data)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_vehicle(override_dependencies):
    """Testa a exclusão de um veículo"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Criar um veículo primeiro
        vehicle_data = {
            "marca": "Chevrolet",
            "modelo": "Onix",
            "ano": 2020,
            "cor": "Vermelho",
            "preco": 55000.00
        }
        create_response = await ac.post("/api/v1/vehicles/", json=vehicle_data)
        vehicle_id = create_response.json()["id"]
        
        # Deletar o veículo
        response = await ac.delete(f"/api/v1/vehicles/{vehicle_id}")
        assert response.status_code == 204
        
        # Verificar que foi deletado
        get_response = await ac.get(f"/api/v1/vehicles/{vehicle_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_vehicle_not_found(override_dependencies):
    """Testa exclusão de veículo inexistente"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/api/v1/vehicles/999")
        assert response.status_code == 404
