from typing import Optional
from datetime import datetime
from pydantic import Field, field_serializer
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
    fecha: datetime = Field(validation_alias="created_at")

    @field_serializer("fecha")
    def serialize_fecha(self, value: datetime, _info) -> str:
        return value.strftime("%d-%m-%Y") if value else ""
