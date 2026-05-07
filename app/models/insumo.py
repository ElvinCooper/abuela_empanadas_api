from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    nombre = Column(String, nullable=False)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="insumos")
    proveedor = relationship("Proveedor", back_populates="insumos")

    @property
    def sucursal_nombre(self):
        return self.sucursal.nombre if self.sucursal else None

    @property
    def proveedor_nombre(self):
        return self.proveedor.nombre if self.proveedor else None
