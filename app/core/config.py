from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Vehicle Management API"
    API_V1_STR: str = "/api/v1"
    
    # Banco de dados transacional (veículos)
    DATABASE_URL: str = "sqlite+aiosqlite:///./vehicles.db"
    
    # Banco de dados de autenticação (separado)
    AUTH_DATABASE_URL: str = "sqlite+aiosqlite:///./auth.db"
    
    # URL do serviço de vendas para comunicação HTTP
    SALES_SERVICE_URL: str = "http://localhost:8001"
    
    # JWT
    SECRET_KEY: str = "development-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
