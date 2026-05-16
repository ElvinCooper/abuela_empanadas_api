from datetime import date as date_type
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, field_validator, model_validator, Field, condecimal
from app.schemas.common import BaseSchema



decimal_field = condecimal(max_digits=10, decimal_places=2)


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
    precio_unitario:  Decimal = decimal_field
    subtotal_linea:   Decimal = decimal_field
    descuento_linea:  Decimal = decimal_field
    base_imponible:   Decimal = decimal_field
    porcentaje_itbis: Decimal = decimal_field
    itbis:            Decimal = decimal_field
    total_linea:      Decimal = decimal_field


class EncabezadoRead(BaseModel):
    id_factura: int
    fecha: str
    id_cliente: int
    moneda: str
    metodo_pago: str
    estado: str
    subtotal: Decimal
    porcentaje_descuento: Decimal
    descuento: Decimal
    base_imponible: Decimal
    total_itbis: Decimal
    total: Decimal


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

    @model_validator(mode="before")
    @classmethod
    def from_orm_factura(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            detalle_items = []
            for d in data.detalles:
                subtotal_linea = d.cantidad * d.precio_unitario
                detalle_items.append(
                    FacturaDetalleItemRead(
                        id_producto=d.producto_id,
                        descripcion=d.producto.nombre if d.producto else "",
                        cantidad=d.cantidad,
                        precio_unitario=Decimal(str(d.precio_unitario)),
                        subtotal_linea=Decimal(str(subtotal_linea)),
                        descuento_linea=Decimal(str(d.descuento or 0)),
                        base_imponible=Decimal(str(d.base_imponible)),
                        porcentaje_itbis=Decimal(str(d.itbis)),
                        itbis=Decimal(str(d.itbis_aplicado)),
                        total_linea=Decimal(str(d.total_linea)),
                    )
                )

            fecha_str = data.created_at.strftime("%Y-%m-%d %H:%M:%S") if data.created_at is not None else ""
            base_imponible = Decimal(str(data.subtotal - data.descuento))

            encabezado = EncabezadoRead(
                id_factura=int(data.id),
                fecha=fecha_str,
                id_cliente=int(data.usuario_id),
                moneda=data.moneda.nombre if data.moneda else "",
                metodo_pago=data.metodo_pago.nombre if data.metodo_pago else "",
                estado=data.status.nombre if data.status else "",
                subtotal=Decimal(str(data.subtotal)),
                porcentaje_descuento=Decimal(str(data.porcentaje_descuento)),
                descuento=Decimal(str(data.descuento)),
                base_imponible=base_imponible,
                total_itbis=Decimal(str(data.itbis)),
                total=Decimal(str(data.total_general)),
            )

            fiscal = FacturaFiscalBlock(
                requiere_ncf=data.ncf is not None,
                ncf=data.ncf,
                tipo_ncf=data.tipo_ncf,
                rnc_emisor=data.rnc_emisor,
                razon_social_emisor=data.razon_social_emisor,
                rnc_cliente=data.rnc_cliente,
                nombre_cliente_fiscal=data.nombre_cliente_fiscal,
                fecha_vencimiento_ncf=(
                    data.fecha_vencimiento_ncf.strftime("%Y-%m-%d")
                    if data.fecha_vencimiento_ncf is not None
                    else None
                ),
                estado_fiscal=data.estado_fiscal,
            )

            return cls.model_validate({
                "encabezado": encabezado.model_dump(),
                "fiscal": fiscal.model_dump(),
                "detalle": detalle_items,
            })
        return data


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
