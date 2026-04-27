from app.schemas.common import BaseSchema


class FacturaCreate(BaseSchema):
    sucursal_id: int
    usuario_id: int
    total: int
    pagada: bool = False


class FacturaUpdate(BaseSchema):
    total: Optional[int] = None
    pagada: Optional[bool] = None


class FacturaRead(BaseSchema):
    id: int
    sucursal_id: int
    usuario_id: int
    total: int
    pagada: bool
