from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.factura import Factura, FacturaDetalle
from app.models.producto import Producto
from app.models.status_factura import StatusFactura
from app.models.anulacion import Anulacion
from app.schemas.factura import (
    FacturaCreate,
    FacturaDataResponse,
    EncabezadoRead,
    FacturaDetalleItemRead,
)
from app.schemas.anulacion import AnulacionCreate, AnulacionRead

router = APIRouter()


def _build_factura_response(factura: Factura) -> FacturaDataResponse:
    detalle_items = []
    for d in factura.detalles:
        detalle_items.append(
            FacturaDetalleItemRead(
                id_producto=d.producto_id,
                cantidad=d.cantidad,
                precio=d.precio_unitario,
                descuento=d.descuento,
                base_imponible=d.base_imponible,
                itbis=d.itbis,
                itbis_aplicado=d.itbis_aplicado,
                total_linea=d.total_linea,
            )
        )

    fecha_str = factura.created_at.strftime("%d-%m-%Y") if factura.created_at else ""

    encabezado = EncabezadoRead(
        id_factura=int(factura.id),
        fecha=fecha_str,
        id_cliente=int(factura.usuario_id),
        subtotal=float(factura.subtotal),
        porcentaje_descuento=float(factura.porcentaje_descuento),
        descuento=float(factura.descuento),
        itbis=float(factura.itbis),
        total_general=float(factura.total_general),
        moneda=factura.moneda.nombre if factura.moneda else "",
        metodo_pago=factura.metodo_pago.nombre if factura.metodo_pago else "",
        estado=factura.status.nombre if factura.status else "",
    )

    return FacturaDataResponse(encabezado=encabezado, detalle=detalle_items)


@router.get("/", response_model=list[FacturaDataResponse])
async def list_facturas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Factura)
        .options(
            selectinload(Factura.sucursal),
            selectinload(Factura.moneda),
            selectinload(Factura.metodo_pago),
            selectinload(Factura.status),
            selectinload(Factura.detalles),
        )
        .order_by(Factura.created_at.desc())
    )
    facturas = result.scalars().all()
    return [_build_factura_response(f) for f in facturas]


@router.post("/", response_model=FacturaDataResponse, status_code=201)
async def create_factura(
    factura: FacturaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    detalle_items_data: list[dict[str, float | int]] = []
    subtotal = 0.0

    for item in factura.detalle:
        producto_result = await db.execute(
            select(Producto).where(Producto.id == item.id_producto)
        )
        producto = producto_result.scalar_one_or_none()
        if producto is None:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con id {item.id_producto} no encontrado",
            )

        precio = int(producto.precio)
        precio_linea = precio * item.cantidad
        descuento_linea = precio_linea * (factura.porcentaje_descuento / 100)
        base_imponible = precio_linea - descuento_linea
        itbis_aplicado = base_imponible * (item.itbis / 100)
        total_linea = base_imponible + itbis_aplicado

        detalle_items_data.append(
            {
                "producto_id": item.id_producto,
                "cantidad": item.cantidad,
                "precio_unitario": precio,
                "descuento": descuento_linea,
                "base_imponible": base_imponible,
                "itbis": item.itbis,
                "itbis_aplicado": itbis_aplicado,
                "total_linea": total_linea,
            }
        )
        subtotal += precio_linea

    descuento_total = subtotal * (factura.porcentaje_descuento / 100)
    base_imponible_total = subtotal - descuento_total
    itbis_total = sum(d["itbis_aplicado"] for d in detalle_items_data)
    total_general = base_imponible_total + itbis_total

    new_factura = Factura(
        sucursal_id=current_user.sucursal_id,
        usuario_id=factura.id_cliente,
        id_status=1,
        id_moneda=factura.id_moneda,
        id_metodo_pago=factura.id_metodo_pago,
        subtotal=subtotal,
        porcentaje_descuento=factura.porcentaje_descuento,
        descuento=descuento_total,
        itbis=itbis_total,
        total_general=total_general,
    )
    db.add(new_factura)
    await db.flush()

    for d_data in detalle_items_data:
        detalle = FacturaDetalle(factura_id=new_factura.id, **d_data)
        db.add(detalle)

    await db.commit()
    await db.refresh(
        new_factura,
        attribute_names=["detalles", "sucursal", "moneda", "metodo_pago", "status"],
    )

    return _build_factura_response(new_factura)


@router.get("/anuladas", response_model=list[AnulacionRead])
async def listar_facturas_anuladas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Anulacion))
    return result.scalars().all()


@router.post("/{factura_id}/anular", response_model=AnulacionRead, status_code=201)
async def anular_factura(
    factura_id: int,
    anulacion: AnulacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    anulada_result = await db.execute(
        select(StatusFactura).where(StatusFactura.nombre == "anulada")
    )
    status_anulada = anulada_result.scalar_one()

    new_anulacion = Anulacion(factura_id=factura_id, motivo=anulacion.motivo)
    db.add(new_anulacion)
    factura = await db.get(Factura, factura_id)
    if factura is not None:
        factura.id_status = status_anulada.id
    await db.commit()
    await db.refresh(new_anulacion)
    return new_anulacion
