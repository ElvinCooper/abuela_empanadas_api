from typing import Optional
from app.schemas.common import BaseSchema


class CategoriaCreate(BaseSchema):
    nombre: str
    descripcion: Optional[str] = None
    icon_img: Optional[str] = None


class CategoriaUpdate(BaseSchema):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    icon_img: Optional[str] = None


class CategoriaRead(BaseSchema):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    icon_img: Optional[str] = None
