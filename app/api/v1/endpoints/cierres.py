from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.cierre_diario import CierreDiario
from app.schemas.cierre import CierreDiarioCreate, CierreDiarioRead

router = APIRouter()


@router.get("/")
async def list_cierres(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        result = await db.execute(select(CierreDiario))
        cierres = result.scalars().all()
        # Convertir manualmente a dicts para evitar errores de serialización
        return [
            {
                "id": c.id,
                "sucursal_id": c.sucursal_id,
                "fecha": str(c.fecha),
                "total_ventas": c.total_ventas,
                "total_egresos": c.total_egresos,
            }
            for c in cierres
        ]
    except Exception as e:
        print(f"Error in list_cierres: {e}")
        raise


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
