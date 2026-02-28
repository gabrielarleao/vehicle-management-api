from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.schemas import VehicleCreate, VehicleResponse, VehicleUpdate
from app.services.vehicle_service import VehicleService
from app.models.vehicle import VehicleStatus

router = APIRouter()


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cadastra um novo veículo para venda.
    
    - **marca**: Marca do veículo (ex: Toyota, Honda, Ford)
    - **modelo**: Modelo do veículo (ex: Corolla, Civic, Focus)
    - **ano**: Ano de fabricação (1900-2100)
    - **cor**: Cor do veículo
    - **preco**: Preço de venda (maior que 0)
    """
    service = VehicleService(db)
    return await service.create_vehicle(vehicle_in)


@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles(
    status: Optional[VehicleStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os veículos.
    
    - Se **status** for informado (DISPONIVEL ou VENDIDO), filtra por status.
    - Sempre ordenado por preço do mais barato para o mais caro.
    """
    service = VehicleService(db)
    return await service.get_vehicles(status)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca um veículo pelo ID.
    """
    service = VehicleService(db)
    vehicle = await service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Edita os dados de um veículo.
    
    Todos os campos são opcionais. Informe apenas os que deseja atualizar.
    """
    service = VehicleService(db)
    vehicle = await service.update_vehicle(vehicle_id, vehicle_in)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Remove um veículo do sistema.
    """
    service = VehicleService(db)
    success = await service.delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
