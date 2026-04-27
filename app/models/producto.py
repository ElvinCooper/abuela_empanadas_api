from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="productos")
    factura_detalles = relationship("FacturaDetalle", back_populates="producto")
