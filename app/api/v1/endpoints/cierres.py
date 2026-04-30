import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.cierre_diario import CierreDiario
from app.schemas.cierre import CierreDiarioCreate, CierreDiarioRead

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def list_cierres(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        result = await db.execute(select(CierreDiario))
        cierres = result.scalars().all()
    except Exception as e:
        logger.exception("Error listing daily closures")
        raise
    return cierres


@router.post("/", response_model=CierreDiarioRead, status_code=201)
async def create_cierre(
    cierre: CierreDiarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_cierre = CierreDiario(
        sucursal_id=cierre.sucursal_id,
        fecha=cierre.fecha,
        total_ventas=cierre.total_ventas,
        total_egresos=cierre.total_egresos,
    )
    db.add(new_cierre)
    await db.commit()
    await db.refresh(new_cierre)
    return new_cierre
