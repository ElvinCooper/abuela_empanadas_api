from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.usuario import Usuario
from app.core.security import verify_password


async def autenticar(
    db: AsyncSession, username: str, password: str
) -> Optional[Usuario]:
    result = await db.execute(
        select(Usuario)
        .where(Usuario.username == username)
        .options(selectinload(Usuario.sucursal))
    )
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):  # type: ignore[arg-type]
        return None
    if not bool(user.activo):
        return None
    return user
