from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class RolEnum(Enum):
    admin = "admin"
    supervisor = "supervisor"
    standard = "standard"
    contable = "contable"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    nombre = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(SQLEnum(RolEnum), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sucursal = relationship("Sucursal", back_populates="usuarios")
