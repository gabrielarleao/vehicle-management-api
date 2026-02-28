from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from app.core.config import settings
from app.routers import vehicles, auth
from app.database import engine, Base, auth_engine, AuthBase
import asyncpg

security = HTTPBearer()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="""
        ## Serviço Principal de Veículos
        
        Este serviço é responsável por:
        
        - **Cadastro de veículos** para venda (marca, modelo, ano, cor, preço)
        - **Edição de veículos** cadastrados
        - **Autenticação de usuários** via JWT
        
        ### Arquitetura
        
        - **Banco Transacional**: Veículos (PostgreSQL)
        - **Banco de Autenticação**: Usuários (PostgreSQL separado)
        
        ### Autenticação
        
        1. Registre-se: POST `/auth/register`
        2. Faça login: POST `/auth/login` (retorna token JWT)
        3. Use o token: Clique em "Authorize" e cole o token
        """,
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    
    # Tentar criar banco de auth no PostgreSQL (quando em Docker)
    try:
        sys_conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            host='vehicle-db',
            database='postgres'
        )
        
        exists = await sys_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'tech_challenge_auth'"
        )
        
        if not exists:
            await sys_conn.execute('CREATE DATABASE tech_challenge_auth')
            print("Banco de dados 'tech_challenge_auth' criado com sucesso!")
        
        await sys_conn.close()
    except Exception as e:
        print(f"Aviso: Usando SQLite local ou banco já existe: {e}")
    
    # Criar tabelas no banco transacional
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Criar tabelas no banco de auth (separado)
    async with auth_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()
    await auth_engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Serviço Principal de Veículos
    
    API para cadastro e gerenciamento de veículos para revenda.
    
    ### Funcionalidades
    
    - Cadastrar veículo para venda
    - Editar dados do veículo
    - Listar veículos (ordenados por preço)
    - Autenticação JWT
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vehicle-management-api"}


# Include routers
app.include_router(
    vehicles.router,
    prefix=f"{settings.API_V1_STR}/vehicles",
    tags=["Veículos"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticação"]
)

app.openapi = custom_openapi
