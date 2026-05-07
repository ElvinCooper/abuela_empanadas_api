from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.metodo_pago import MetodoPago
from app.schemas.metodo_pago import MetodoPagoCreate, MetodoPagoRead

router = APIRouter()


@router.get("/", response_model=list[MetodoPagoRead])
async def list_metodos_pago(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(MetodoPago))
    return result.scalars().all()


@router.post("/", response_model=MetodoPagoRead, status_code=201)
async def create_metodo_pago(
    metodo_pago: MetodoPagoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_metodo_pago = MetodoPago(
        nombre=metodo_pago.nombre,
        descripcion=metodo_pago.descripcion,
        activo=True,
    )
    db.add(new_metodo_pago)
    await db.commit()
    await db.refresh(new_metodo_pago)
    return new_metodo_pago
