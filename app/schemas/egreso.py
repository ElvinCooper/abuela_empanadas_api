from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema


class EgresoCreate(BaseSchema):
    sucursal_id: int
    descripcion: str
    monto: int


class EgresoUpdate(BaseSchema):
    descripcion: Optional[str] = None
    monto: Optional[int] = None


class EgresoRead(BaseSchema):
    id: int
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    descripcion: str
    monto: int
    created_at: datetime
