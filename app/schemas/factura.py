from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, computed_field, field_validator
from app.schemas.common import BaseSchema


class FacturaFiscalInput(BaseModel):
    ncf: Optional[str] = None
    tipo_ncf: Optional[str] = None
    rnc_cliente: Optional[str] = None
    nombre_cliente_fiscal: Optional[str] = None
    fecha_vencimiento_ncf: Optional[str] = None

    @field_validator("ncf")
    @classmethod
    def validar_ncf(cls, v):
        if v is not None and len(v) > 19:
            raise ValueError("ncf debe tener maximo 19 caracteres")
        return v

    @field_validator("tipo_ncf")
    @classmethod
    def validar_tipo_ncf(cls, v):
        if v is not None and len(v) > 5:
            raise ValueError("tipo_ncf debe tener maximo 5 caracteres")
        return v

    @field_validator("rnc_cliente")
    @classmethod
    def validar_rnc_cliente(cls, v):
        if v is not None and len(v) > 9:
            raise ValueError("rnc_cliente debe tener maximo 9 caracteres")
        return v

    @field_validator("fecha_vencimiento_ncf")
    @classmethod
    def validar_fecha_formato(cls, v):
        if v is None or v == "":
            return None
        try:
            date_type.fromisoformat(v)
        except ValueError:
            raise ValueError("fecha_vencimiento_ncf debe estar en formato YYYY-MM-DD")
        return v


class FacturaDetalleItemCreate(BaseModel):
    id_producto: int
    cantidad: int
    itbis: float = 0.0
    precio_unitario: Optional[float] = None
    descuento: Optional[float] = None


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


class FacturaFiscalBlock(BaseModel):
    requiere_ncf: bool = False
    ncf: Optional[str] = None
    tipo_ncf: Optional[str] = None
    rnc_emisor: Optional[str] = None
    razon_social_emisor: Optional[str] = None
    rnc_cliente: Optional[str] = None
    nombre_cliente_fiscal: Optional[str] = None
    fecha_vencimiento_ncf: Optional[str] = None
    estado_fiscal: Optional[str] = None


class FacturaDataResponse(BaseModel):
    encabezado: EncabezadoRead
    fiscal: FacturaFiscalBlock
    detalle: list[FacturaDetalleItemRead]


class FacturaCreate(BaseModel):
    id_cliente: int
    id_moneda: int = 1
    id_metodo_pago: int = 1
    porcentaje_descuento: float = 0.0
    fiscal: Optional[FacturaFiscalInput] = None
    detalle: list[FacturaDetalleItemCreate]


class FacturaUpdate(BaseModel):
    id_moneda: Optional[int] = None
    id_metodo_pago: Optional[int] = None
    porcentaje_descuento: Optional[float] = None
