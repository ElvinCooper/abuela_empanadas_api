from typing import Optional
from datetime import datetime
from pydantic import field_serializer
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
    created_at: str

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime, _info):
        return value.strftime("%d-%m-%Y") if value else ""
