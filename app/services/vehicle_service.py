from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.schemas import VehicleCreate, VehicleUpdate


class VehicleService:
    """Serviço para gerenciamento de veículos (CRUD)"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_vehicle(self, vehicle_in: VehicleCreate) -> Vehicle:
        """Cria um novo veículo"""
        vehicle = Vehicle(**vehicle_in.model_dump())
        self.db.add(vehicle)
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle

    async def get_vehicles(self, status: VehicleStatus = None) -> list[Vehicle]:
        """
        Lista veículos ordenados por preço (menor para maior).
        Opcionalmente filtra por status.
        """
        query = select(Vehicle)
        if status:
            query = query.where(Vehicle.status == status)
        
        # Requisito: ordenar por preço do mais barato para o mais caro
        query = query.order_by(asc(Vehicle.preco))
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_vehicle(self, vehicle_id: int) -> Vehicle | None:
        """Busca veículo por ID"""
        result = await self.db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        return result.scalar_one_or_none()

    async def update_vehicle(self, vehicle_id: int, vehicle_in: VehicleUpdate) -> Vehicle | None:
        """Atualiza dados de um veículo"""
        vehicle = await self.get_vehicle(vehicle_id)
        if not vehicle:
            return None
        
        update_data = vehicle_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehicle, key, value)
        
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle

    async def delete_vehicle(self, vehicle_id: int) -> bool:
        """Deleta um veículo"""
        vehicle = await self.get_vehicle(vehicle_id)
        if not vehicle:
            return False
        
        await self.db.delete(vehicle)
        await self.db.commit()
        return True
