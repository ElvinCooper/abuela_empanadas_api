from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.schemas.factura import FacturaCreate, FacturaRead
from app.schemas.anulacion import AnulacionCreate, AnulacionRead

router = APIRouter()


@router.get("/", response_model=list[FacturaRead])
async def list_facturas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/", response_model=FacturaRead, status_code=201)
async def create_factura(
    factura: FacturaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.get("/anuladas", response_model=list[AnulacionRead])
async def listar_facturas_anuladas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/{factura_id}/anular", response_model=AnulacionRead, status_code=201)
async def anular_factura(
    factura_id: int,
    anulacion: AnulacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
