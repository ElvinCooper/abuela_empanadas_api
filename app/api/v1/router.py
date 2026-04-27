from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    usuarios,
    sucursales,
    productos,
    facturas,
    anulaciones,
    cierres,
    egresos,
    proveedores,
    insumos,
    reportes,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(sucursales.router, prefix="/sucursales", tags=["sucursales"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(facturas.router, prefix="/facturas", tags=["facturas"])
api_router.include_router(
    anulaciones.router, prefix="/anulaciones", tags=["anulaciones"]
)
api_router.include_router(cierres.router, prefix="/cierres", tags=["cierres"])
api_router.include_router(egresos.router, prefix="/egresos", tags=["egresos"])
api_router.include_router(
    proveedores.router, prefix="/proveedores", tags=["proveedores"]
)
api_router.include_router(insumos.router, prefix="/insumos", tags=["insumos"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["reportes"])
