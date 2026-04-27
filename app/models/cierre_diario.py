from sqlalchemy import Column, Integer, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class CierreDiario(Base):
    __tablename__ = "cierres_diarios"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False)
    total_ventas = Column(Integer, nullable=False)
    total_egresos = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="cierres")
