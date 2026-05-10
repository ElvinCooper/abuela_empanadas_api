from typing import Optional
from app.schemas.common import BaseSchema


class ProductoCreate(BaseSchema):
    sucursal_id: int
    categoria_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    precio: int
    stock: int = 0
    icon_img: Optional[str] = None


class ProductoUpdate(BaseSchema):
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    activo: Optional[bool] = None


class ProductoRead(BaseSchema):
    id: int
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    categoria_nombre: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    precio: int
    stock: int
    activo: bool
    icon_img: Optional[str] = None
