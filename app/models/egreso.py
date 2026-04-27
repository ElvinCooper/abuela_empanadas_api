from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Egreso(Base):
    __tablename__ = "egresos"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    descripcion = Column(String, nullable=False)
    monto = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="egresos")
