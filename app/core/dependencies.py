from typing import Callable, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.core.security import verify_token
from app.db.session import AsyncSessionLocal
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    try:
        user_id_int = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    result = await db.execute(
        select(Usuario)
        .where(Usuario.id == user_id_int)
        .options(selectinload(Usuario.sucursal))
    )
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    if not bool(user.activo):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return user


def require_roles(*roles: str) -> Callable:
    async def role_checker(current_user: Usuario = Depends(get_current_user)):
        # Convertir rol del usuario a string para comparar con los roles permitidos
        user_rol = (
            current_user.rol.value
            if hasattr(current_user.rol, "value")
            else str(current_user.rol)
        )
        if user_rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
