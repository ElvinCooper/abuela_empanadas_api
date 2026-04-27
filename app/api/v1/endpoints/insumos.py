from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.insumo import InsumoCreate, InsumoRead

router = APIRouter()


@router.get("/", response_model=list[InsumoRead])
async def list_insumos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/", response_model=InsumoRead, status_code=201)
async def create_insumo(
    insumo: InsumoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
