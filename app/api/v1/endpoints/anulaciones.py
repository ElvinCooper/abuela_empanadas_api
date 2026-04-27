from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.anulacion import AnulacionCreate, AnulacionRead

router = APIRouter()


@router.get("/", response_model=list[AnulacionRead])
async def list_anulaciones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/", response_model=AnulacionRead, status_code=201)
async def create_anulacion(
    anulacion: AnulacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
