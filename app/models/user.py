from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import AuthBase


class User(AuthBase):
    """
    Modelo de usuário para autenticação.
    Armazenado em banco de dados SEPARADO (auth).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
