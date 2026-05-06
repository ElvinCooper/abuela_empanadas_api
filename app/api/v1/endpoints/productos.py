from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoRead

router = APIRouter()


@router.get("/", response_model=list[ProductoRead])
async def list_productos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Producto).options(selectinload(Producto.sucursal)))
    productos = result.scalars().all()
    return productos


@router.post("/", response_model=ProductoRead, status_code=201)
async def create_producto(
    producto: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_producto = Producto(
        sucursal_id=producto.sucursal_id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        stock=producto.stock,
        activo=True,
    )
    db.add(new_producto)
    await db.commit()
    await db.refresh(new_producto, attribute_names=["sucursal"])
    return new_producto


@router.post("/", response_model=ProductoRead, status_code=201)
async def create_producto(
    producto: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    raise NotImplementedError
