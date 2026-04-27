from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user, require_roles
from app.schemas.usuario import UsuarioCreate, UsuarioRead
from app.models.usuario import Usuario

router = APIRouter()


@router.get("/", response_model=list[UsuarioRead])
async def list_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_roles("admin", "supervisor")),
):
    raise NotImplementedError


@router.post("/", response_model=UsuarioRead, status_code=201)
async def create_usuario(
    usuario: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_roles("admin")),
):
    raise NotImplementedError
