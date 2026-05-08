from datetime import date
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_status = Column(
        Integer,
        ForeignKey("status_factura.id"),
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    id_moneda = Column(
        Integer,
        ForeignKey("monedas.id"),
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    id_metodo_pago = Column(
        Integer,
        ForeignKey("metodo_pago.id"),
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    subtotal = Column(Float, nullable=False)
    porcentaje_descuento = Column(
        Float, nullable=False, server_default=text("0"), default=0
    )
    descuento = Column(Float, nullable=False, server_default=text("0"), default=0)
    itbis = Column(Float, nullable=False, server_default=text("0"), default=0)
    total_general = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ncf = Column(String(19), nullable=True)
    tipo_ncf = Column(String(5), nullable=True)
    rnc_emisor = Column(String(9), nullable=True)
    razon_social_emisor = Column(String(200), nullable=True)
    rnc_cliente = Column(String(9), nullable=True)
    nombre_cliente_fiscal = Column(String(200), nullable=True)
    fecha_vencimiento_ncf = Column(Date, nullable=True)
    estado_fiscal = Column(String(20), nullable=True)

    sucursal = relationship("Sucursal", back_populates="facturas")
    usuario = relationship("Usuario")
    status = relationship("StatusFactura", back_populates="facturas")
    moneda = relationship("Moneda", back_populates="facturas")
    metodo_pago = relationship("MetodoPago", back_populates="facturas")
    detalles = relationship("FacturaDetalle", back_populates="factura")
    anulaciones = relationship("Anulacion", back_populates="factura")

    @property
    def sucursal_nombre(self):
        return self.sucursal.nombre if self.sucursal else None


class FacturaDetalle(Base):
    __tablename__ = "factura_detalles"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    descuento = Column(Float, nullable=False, server_default=text("0"), default=0)
    base_imponible = Column(Float, nullable=False)
    itbis = Column(Float, nullable=False, server_default=text("0"), default=0)
    itbis_aplicado = Column(Float, nullable=False, server_default=text("0"), default=0)
    total_linea = Column(Float, nullable=False)

    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="factura_detalles")
