from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.vehicle import VehicleStatus


# ============ Vehicle Schemas ============

class VehicleBase(BaseModel):
    marca: str = Field(..., min_length=1, max_length=100)
    modelo: str = Field(..., min_length=1, max_length=100)
    ano: int = Field(..., ge=1900, le=2100)
    cor: str = Field(..., min_length=1, max_length=50)
    preco: float = Field(..., gt=0)


class VehicleCreate(VehicleBase):
    """Schema para criação de veículo"""
    pass


class VehicleUpdate(BaseModel):
    """Schema para atualização de veículo (todos campos opcionais)"""
    marca: Optional[str] = Field(None, min_length=1, max_length=100)
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    ano: Optional[int] = Field(None, ge=1900, le=2100)
    cor: Optional[str] = Field(None, min_length=1, max_length=50)
    preco: Optional[float] = Field(None, gt=0)
    status: Optional[VehicleStatus] = None


class VehicleResponse(VehicleBase):
    """Schema de resposta para veículo"""
    id: int
    status: VehicleStatus
    data_cadastro: datetime

    class Config:
        from_attributes = True


# ============ User Schemas ============

class UserCreate(BaseModel):
    """Schema para registro de usuário"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de resposta para usuário"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema de resposta para token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Dados extraídos do token"""
    user_id: Optional[int] = None
