from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema
from pydantic import field_serializer


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
    created_at: Optional[datetime] = None

    @field_serializer("fecha")
    def format_fecha(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")

    @field_serializer("created_at")
    def format_created_at(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M")
