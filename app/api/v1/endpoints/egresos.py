from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.egreso import Egreso
from app.schemas.egreso import EgresoCreate, EgresoRead

router = APIRouter()


@router.get("/", response_model=list[EgresoRead])
async def listar_gastos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Egreso))
    return result.scalars().all()


@router.post("/", response_model=EgresoRead, status_code=201)
async def crear_gasto(
    egreso: EgresoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_egreso = Egreso(
        sucursal_id=egreso.sucursal_id,
        descripcion=egreso.descripcion,
        monto=egreso.monto,
    )
    db.add(new_egreso)
    await db.commit()
    await db.refresh(new_egreso)
    return new_egreso
