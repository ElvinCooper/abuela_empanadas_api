from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.schemas.producto import ProductoCreate, ProductoRead

router = APIRouter()


@router.get("/", response_model=list[ProductoRead])
async def list_productos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).options(
            selectinload(Producto.sucursal), selectinload(Producto.categoria)
        )
    )
    productos = result.scalars().all()
    return productos


@router.get("/categoria/{categoria_id}", response_model=list[ProductoRead])
async def list_productos_by_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    categoria_result = await db.execute(
        select(Categoria).where(Categoria.id == categoria_id)
    )
    categoria = categoria_result.scalar_one_or_none()
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    result = await db.execute(
        select(Producto)
        .where(Producto.categoria_id == categoria_id)
        .options(selectinload(Producto.sucursal), selectinload(Producto.categoria))
    )
    return result.scalars().all()


@router.post("/", response_model=ProductoRead, status_code=201)
async def create_producto(
    producto: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_producto = Producto(
        sucursal_id=producto.sucursal_id,
        categoria_id=producto.categoria_id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        stock=producto.stock,
        activo=True,
    )
    db.add(new_producto)
    await db.commit()
    await db.refresh(new_producto, attribute_names=["sucursal", "categoria"])
    return new_producto
