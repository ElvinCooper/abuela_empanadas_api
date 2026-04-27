from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    total = Column(Integer, nullable=False)
    pagada = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="facturas")
    usuario = relationship("Usuario")
    detalles = relationship("FacturaDetalle", back_populates="factura")


class FacturaDetalle(Base):
    __tablename__ = "factura_detalles"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Integer, nullable=False)

    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="factura_detalles")
