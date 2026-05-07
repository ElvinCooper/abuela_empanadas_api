from typing import Optional
from app.schemas.common import BaseSchema


class MetodoPagoCreate(BaseSchema):
    nombre: str
    descripcion: Optional[str] = None


class MetodoPagoUpdate(BaseSchema):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class MetodoPagoRead(BaseSchema):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
