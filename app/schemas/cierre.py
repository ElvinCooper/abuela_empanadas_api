from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema


class CierreDiarioCreate(BaseSchema):
    sucursal_id: int
    fecha: datetime
    total_ventas: int
    total_egresos: int


class CierreDiarioUpdate(BaseSchema):
    total_ventas: Optional[int] = None
    total_egresos: Optional[int] = None


class CierreDiarioRead(BaseSchema):
    id: int
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    fecha: datetime
    total_ventas: int
    total_egresos: int
