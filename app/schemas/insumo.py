from typing import Optional
from app.schemas.common import BaseSchema


class InsumoCreate(BaseSchema):
    sucursal_id: int
    proveedor_id: Optional[int] = None
    nombre: str
    stock: int = 0


class InsumoUpdate(BaseSchema):
    nombre: Optional[str] = None
    stock: Optional[int] = None
    activo: Optional[bool] = None


class InsumoRead(BaseSchema):
    id: int
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    proveedor_id: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    nombre: str
    stock: Optional[int] = None
    activo: bool
