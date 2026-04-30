from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.proveedor import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorRead

router = APIRouter()


@router.get("/", response_model=list[ProveedorRead])
async def list_proveedores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Proveedor))
    return result.scalars().all()


@router.post("/", response_model=ProveedorRead, status_code=201)
async def create_proveedor(
    proveedor: ProveedorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_proveedor = Proveedor(
        nombre=proveedor.nombre,
        contacto=proveedor.contacto,
        telefono=proveedor.telefono,
        activo=True,
    )
    db.add(new_proveedor)
    await db.commit()
    await db.refresh(new_proveedor)
    return new_proveedor
