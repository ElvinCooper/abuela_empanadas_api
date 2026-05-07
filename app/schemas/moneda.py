from typing import Optional
from app.schemas.common import BaseSchema


class MonedaCreate(BaseSchema):
    nombre: str
    simbolo: str
    descripcion: Optional[str] = None


class MonedaUpdate(BaseSchema):
    nombre: Optional[str] = None
    simbolo: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class MonedaRead(BaseSchema):
    id: int
    nombre: str
    simbolo: str
    descripcion: Optional[str] = None
    activo: bool
