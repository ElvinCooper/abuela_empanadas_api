from typing import Optional
from pydantic import BaseModel, computed_field
from app.schemas.common import BaseSchema


class FacturaDetalleItemCreate(BaseModel):
    id_producto: int
    cantidad: int
    itbis: int = 0


class FacturaDetalleItemRead(BaseModel):
    id_producto: int
    cantidad: int
    precio: float
    descuento: float
    base_imponible: float
    itbis: float
    itbis_aplicado: float
    total_linea: float


class EncabezadoRead(BaseModel):
    id_factura: int
    fecha: str
    id_cliente: int
    subtotal: float
    porcentaje_descuento: float
    descuento: float
    itbis: float
    total_general: float
    moneda: str
    metodo_pago: str
    estado: str


class FacturaDataResponse(BaseModel):
    encabezado: EncabezadoRead
    detalle: list[FacturaDetalleItemRead]


class FacturaCreate(BaseModel):
    id_cliente: int
    id_moneda: int = 1
    id_metodo_pago: int = 1
    porcentaje_descuento: float = 0.0
    detalle: list[FacturaDetalleItemCreate]


class FacturaUpdate(BaseModel):
    id_moneda: Optional[int] = None
    id_metodo_pago: Optional[int] = None
    porcentaje_descuento: Optional[float] = None
