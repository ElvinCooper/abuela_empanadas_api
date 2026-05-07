from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.moneda import Moneda
from app.schemas.moneda import MonedaCreate, MonedaRead

router = APIRouter()


@router.get("/", response_model=list[MonedaRead])
async def list_monedas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Moneda))
    return result.scalars().all()


@router.post("/", response_model=MonedaRead, status_code=201)
async def create_moneda(
    moneda: MonedaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_moneda = Moneda(
        nombre=moneda.nombre,
        simbolo=moneda.simbolo,
        descripcion=moneda.descripcion,
        activo=True,
    )
    db.add(new_moneda)
    await db.commit()
    await db.refresh(new_moneda)
    return new_moneda
