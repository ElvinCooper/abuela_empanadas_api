from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import TokenResponse
from app.schemas.usuario import UsuarioRead
from app.services.auth_service import autenticar
from app.models.usuario import Usuario

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await autenticar(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(user.id), "rol": user.rol})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": user,
    }


@router.get("/me", response_model=UsuarioRead)
async def read_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    return None
