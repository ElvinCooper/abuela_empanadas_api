from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.factura import Factura
from app.models.anulacion import Anulacion
from app.schemas.factura import FacturaCreate, FacturaRead
from app.schemas.anulacion import AnulacionCreate, AnulacionRead

router = APIRouter()


@router.get("/", response_model=list[FacturaRead])
async def list_facturas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Factura))
    return result.scalars().all()


@router.post("/", response_model=FacturaRead, status_code=201)
async def create_factura(
    factura: FacturaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_factura = Factura(
        sucursal_id=factura.sucursal_id,
        usuario_id=factura.usuario_id,
        total=factura.total,
        pagada=factura.pagada,
    )
    db.add(new_factura)
    await db.commit()
    await db.refresh(new_factura)
    return new_factura


@router.get("/anuladas", response_model=list[AnulacionRead])
async def listar_facturas_anuladas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Anulacion))
    return result.scalars().all()


@router.post("/{factura_id}/anular", response_model=AnulacionRead, status_code=201)
async def anular_factura(
    factura_id: int,
    anulacion: AnulacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_anulacion = Anulacion(factura_id=factura_id, motivo=anulacion.motivo)
    db.add(new_anulacion)
    await db.commit()
    await db.refresh(new_anulacion)
    return new_anulacion
