import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
from app.database import Base


class VehicleStatus(str, enum.Enum):
    DISPONIVEL = "DISPONIVEL"
    VENDIDO = "VENDIDO"


class Vehicle(Base):
    """
    Modelo de veículo para cadastro e gerenciamento.
    Este é o modelo principal, armazenado no banco transacional.
    """
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, index=True, nullable=False)
    modelo = Column(String, index=True, nullable=False)
    ano = Column(Integer, nullable=False)
    cor = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.DISPONIVEL)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
