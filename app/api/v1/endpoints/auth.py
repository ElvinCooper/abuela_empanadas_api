from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import TokenResponse
from app.schemas.usuario import UsuarioRead
from app.services.auth_service import autenticar
from app.models.usuario import Usuario
from app.core.logging_config import get_logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = get_logger(__name__)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Login attempt received")
    user = await autenticar(db, username, password)
    if not user:
        logger.warning("Login failed for unknown credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    from app.core.security import create_access_token

    logger.info("Login successful")
    access_token = create_access_token(data={"sub": str(user.id), "rol": user.rol})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": user,
    }


@router.get("/me", response_model=UsuarioRead)
async def read_me(current_user: Usuario = Depends(get_current_user)):
    logger.info("User info requested")
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    logger.info("User session closed")
    return None
