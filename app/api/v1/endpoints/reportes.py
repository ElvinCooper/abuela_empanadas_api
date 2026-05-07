from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.factura import Factura
from app.models.egreso import Egreso

router = APIRouter()


@router.get("/")
async def generate_reporte(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Reporte básico: total de ventas y gastos
    facturas_result = await db.execute(select(func.sum(Factura.total_general)))
    total_ventas = facturas_result.scalar() or 0

    gastos_result = await db.execute(select(func.sum(Egreso.monto)))
    total_gastos = gastos_result.scalar() or 0

    return {
        "total_ventas": total_ventas,
        "total_gastos": total_gastos,
        "utilidad": total_ventas - total_gastos,
    }
