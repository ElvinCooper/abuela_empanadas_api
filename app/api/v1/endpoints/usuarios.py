from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user, require_roles
from app.core.security import hash_password
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.models.usuario import Usuario

router = APIRouter()


@router.get("/", response_model=list[UsuarioRead])
async def list_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_roles("admin", "supervisor")),
):
    result = await db.execute(select(Usuario).options(selectinload(Usuario.sucursal)))
    return result.scalars().all()


@router.post("/", response_model=UsuarioRead, status_code=201)
async def create_usuario(
    usuario: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_roles("admin")),
):
    new_usuario = Usuario(
        sucursal_id=usuario.sucursal_id,
        nombre=usuario.nombre if usuario.nombre else usuario.username,
        username=usuario.username,
        password_hash=hash_password(usuario.password),
        rol=usuario.rol,
        activo=True,
    )
    db.add(new_usuario)
    await db.commit()
    await db.refresh(new_usuario, attribute_names=["sucursal"])
    return new_usuario
