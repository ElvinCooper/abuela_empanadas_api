from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate

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


@router.put("/{categoria_id}", response_model=CategoriaRead)
async def update_categoria(
    categoria_id: int,
    categoria: CategoriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    db_categoria = result.scalar_one_or_none()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if categoria.nombre is not None:
        db_categoria.nombre = categoria.nombre
    if categoria.descripcion is not None:
        db_categoria.descripcion = categoria.descripcion

    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria
