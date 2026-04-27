from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Sucursal(Base):
    __tablename__ = "sucursales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuarios = relationship("Usuario", back_populates="sucursal")
    productos = relationship("Producto", back_populates="sucursal")
    facturas = relationship("Factura", back_populates="sucursal")
    cierres = relationship("CierreDiario", back_populates="sucursal")
    egresos = relationship("Egreso", back_populates="sucursal")
    insumos = relationship("Insumo", back_populates="sucursal")
