from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.sucursal import Sucursal
from app.schemas.sucursal import SucursalCreate, SucursalRead

router = APIRouter()


@router.get("/", response_model=list[SucursalRead])
async def list_sucursales(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Sucursal))
    sucursales = result.scalars().all()
    return sucursales


@router.post("/", response_model=SucursalRead, status_code=201)
async def create_sucursal(
    sucursal: SucursalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_sucursal = Sucursal(
        nombre=sucursal.nombre,
        direccion=sucursal.direccion,
        telefono=sucursal.telefono,
        activo=True,
    )
    db.add(new_sucursal)
    await db.commit()
    await db.refresh(new_sucursal)
    return new_sucursal
