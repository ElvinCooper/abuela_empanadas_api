from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Anulacion(Base):
    __tablename__ = "anulaciones"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    motivo = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    factura = relationship("Factura")
