from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.factura import FacturaCreate, FacturaRead

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
