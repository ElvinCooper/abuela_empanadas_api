from typing import Optional
from pydantic import BaseModel, computed_field
from app.schemas.common import BaseSchema


class FacturaDetalleItemCreate(BaseModel):
    id_producto: int
    cantidad: int
    itbis: int = 0


class FacturaDetalleItemRead(BaseModel):
    id_producto: int
    descripcion: str
    cantidad: int
    precio_unitario: float
    subtotal_linea: float
    descuento_linea: float
    base_imponible: float
    porcentaje_itbis: float
    itbis: float
    total_linea: float


class EncabezadoRead(BaseModel):
    id_factura: int
    fecha: str
    id_cliente: int
    moneda: str
    metodo_pago: str
    estado: str
    subtotal: float
    porcentaje_descuento: float
    descuento: float
    base_imponible: float
    total_itbis: float
    total: float


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
