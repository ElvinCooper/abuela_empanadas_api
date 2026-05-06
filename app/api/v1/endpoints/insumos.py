from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.insumo import Insumo
from app.schemas.insumo import InsumoCreate, InsumoRead

router = APIRouter()


@router.get("/", response_model=list[InsumoRead])
async def list_insumos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Insumo).options(selectinload(Insumo.sucursal)))
    return result.scalars().all()


@router.post("/", response_model=InsumoRead, status_code=201)
async def create_insumo(
    insumo: InsumoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_insumo = Insumo(
        sucursal_id=insumo.sucursal_id,
        proveedor_id=insumo.proveedor_id,
        nombre=insumo.nombre,
        stock=insumo.stock,
        activo=True,
    )
    db.add(new_insumo)
    await db.commit()
    await db.refresh(new_insumo, attribute_names=["sucursal"])
    return new_insumo
