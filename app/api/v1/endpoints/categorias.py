from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.schemas.categoria import CategoriaCreate, CategoriaRead
from app.schemas.producto import ProductoRead

router = APIRouter()


@router.get("/", response_model=list[CategoriaRead])
async def list_categorias(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Categoria))
    return result.scalars().all()


@router.post("/", response_model=CategoriaRead, status_code=201)
async def create_categoria(
    categoria: CategoriaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_categoria = Categoria(
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
        activo=True,
    )
    db.add(new_categoria)
    await db.commit()
    await db.refresh(new_categoria)
    return new_categoria


@router.get("/{categoria_id}/productos", response_model=list[ProductoRead])
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
