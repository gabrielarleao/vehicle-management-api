from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_auth_db
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.user_service import UserService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_auth_db)
):
    """
    Registra um novo usuário no sistema.
    
    - **email**: Email único do usuário
    - **password**: Senha (mínimo 6 caracteres)
    - **full_name**: Nome completo (opcional)
    """
    service = UserService(db)
    return await service.create_user(user_in)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_auth_db)
):
    """
    Autentica um usuário e retorna um token JWT.
    
    Use o token retornado no header Authorization das próximas requisições:
    `Authorization: Bearer <token>`
    """
    service = UserService(db)
    return await service.authenticate_user(login_data)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os dados do usuário autenticado.
    
    **Requer autenticação JWT.**
    """
    return current_user
