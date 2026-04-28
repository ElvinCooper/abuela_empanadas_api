from typing import Optional
from app.schemas.common import BaseSchema


class ProveedorCreate(BaseSchema):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None


class ProveedorUpdate(BaseSchema):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class ProveedorRead(BaseSchema):
    id: int
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool
