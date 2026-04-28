from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.schemas.sucursal import SucursalCreate, SucursalRead

router = APIRouter()


@router.get("/", response_model=list[SucursalRead])
async def list_sucursales(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/", response_model=SucursalRead, status_code=201)
async def create_sucursal(
    sucursal: SucursalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
