from typing import Optional
from datetime import datetime
from pydantic import computed_field
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

    @computed_field
    def fecha(self) -> str:
        return self.created_at.strftime("%d-%m-%Y") if self.created_at else ""
