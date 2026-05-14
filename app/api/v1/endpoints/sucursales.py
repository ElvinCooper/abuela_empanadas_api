from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.sucursal import Sucursal
from app.schemas.sucursal import SucursalCreate, SucursalRead, SucursalUpdate

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


@router.patch("/{sucursal_id}", response_model=SucursalRead)
async def update_sucursal(
    sucursal_id: int,
    sucursal_update: SucursalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    sucursal = await db.get(Sucursal, sucursal_id)
    if sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    update_data = sucursal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sucursal, field, value)

    await db.commit()
    await db.refresh(sucursal)
    return sucursal
