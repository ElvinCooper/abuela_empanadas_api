from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.schemas.egreso import EgresoCreate, EgresoRead

router = APIRouter()


@router.get("/", response_model=list[EgresoRead])
async def listar_gastos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/", response_model=EgresoRead, status_code=201)
async def crear_gasto(
    egreso: EgresoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
