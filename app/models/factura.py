from sqlalchemy import Column, DateTime, ForeignKey, Integer, text
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
    total = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="facturas")
    usuario = relationship("Usuario")
    status = relationship("StatusFactura", back_populates="facturas")
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
    precio_unitario = Column(Integer, nullable=False)

    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="factura_detalles")
