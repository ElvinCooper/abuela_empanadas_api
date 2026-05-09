from typing import Optional
from app.schemas.common import BaseSchema
from app.models.usuario import RolEnum


class UsuarioCreate(BaseSchema):
    sucursal_id: int
    nombre: Optional[str] = None
    username: str
    password: str
    rol: RolEnum


class UsuarioUpdate(BaseSchema):
    nombre: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[RolEnum] = None
    activo: Optional[bool] = None


class UsuarioRead(BaseSchema):
    id: int
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    nombre: str
    username: str
    rol: RolEnum
    activo: bool
