from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.proveedor import ProveedorCreate, ProveedorRead

router = APIRouter()


@router.get("/", response_model=list[ProveedorRead])
async def list_proveedores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError


@router.post("/", response_model=ProveedorRead, status_code=201)
async def create_proveedor(
    proveedor: ProveedorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
