from app.schemas.common import BaseSchema
from typing import Optional


class SucursalCreate(BaseSchema):
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None


class SucursalUpdate(BaseSchema):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class SucursalRead(BaseSchema):
    id: int
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool
