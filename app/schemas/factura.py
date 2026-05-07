from typing import Optional
from app.schemas.common import BaseSchema


class FacturaCreate(BaseSchema):
    sucursal_id: int
    usuario_id: int
    total: int
    id_status: int = 1
    id_moneda: int = 1
    id_metodo_pago: int = 1
    descuento: int = 0


class FacturaUpdate(BaseSchema):
    total: Optional[int] = None
    id_status: Optional[int] = None
    id_moneda: Optional[int] = None
    id_metodo_pago: Optional[int] = None
    descuento: Optional[int] = None


class FacturaRead(BaseSchema):
    id: int
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    usuario_id: int
    id_status: int
    id_moneda: int
    id_metodo_pago: int
    total: int
    descuento: int
