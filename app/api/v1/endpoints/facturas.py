from datetime import date as date_type, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
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
    FacturaFiscalBlock,
)
from app.schemas.anulacion import AnulacionCreate, AnulacionRead

router = APIRouter()


def _build_factura_response(factura: Factura) -> FacturaDataResponse:
    detalle_items = []
    for d in factura.detalles:
        subtotal_linea = d.cantidad * d.precio_unitario
        detalle_items.append(
            FacturaDetalleItemRead(
                id_producto=d.producto_id,
                descripcion=d.producto.nombre if d.producto else "",
                cantidad=d.cantidad,
                precio_unitario=float(d.precio_unitario),
                subtotal_linea=float(subtotal_linea),
                descuento_linea=float(d.descuento),
                base_imponible=float(d.base_imponible),
                porcentaje_itbis=float(d.itbis),
                itbis=float(d.itbis_aplicado),
                total_linea=float(d.total_linea),
            )
        )

    fecha_str = factura.created_at.strftime("%Y-%m-%d %H:%M:%S") if factura.created_at else ""
    base_imponible = float(factura.subtotal - factura.descuento)

    encabezado = EncabezadoRead(
        id_factura=int(factura.id),
        fecha=fecha_str,
        id_cliente=int(factura.usuario_id),
        moneda=factura.moneda.nombre if factura.moneda else "",
        metodo_pago=factura.metodo_pago.nombre if factura.metodo_pago else "",
        estado=factura.status.nombre if factura.status else "",
        subtotal=float(factura.subtotal),
        porcentaje_descuento=float(factura.porcentaje_descuento),
        descuento=float(factura.descuento),
        base_imponible=base_imponible,
        total_itbis=float(factura.itbis),
        total=float(factura.total_general),
    )

    fiscal = FacturaFiscalBlock(
        requiere_ncf=factura.ncf is not None,
        ncf=factura.ncf,  # type: ignore[arg-type]
        tipo_ncf=factura.tipo_ncf,  # type: ignore[arg-type]
        rnc_emisor=factura.rnc_emisor,  # type: ignore[arg-type]
        razon_social_emisor=factura.razon_social_emisor,  # type: ignore[arg-type]
        rnc_cliente=factura.rnc_cliente,  # type: ignore[arg-type]
        nombre_cliente_fiscal=factura.nombre_cliente_fiscal,  # type: ignore[arg-type]
        fecha_vencimiento_ncf=(
            factura.fecha_vencimiento_ncf.strftime("%Y-%m-%d")
            if factura.fecha_vencimiento_ncf
            else None
        ),
        estado_fiscal=factura.estado_fiscal,  # type: ignore[arg-type]
    )

    return FacturaDataResponse(encabezado=encabezado, fiscal=fiscal, detalle=detalle_items)


@router.get("/", response_model=list[FacturaDataResponse])
async def list_facturas(
    fecha_inicio: date_type = Query(..., description="Fecha inicial del rango (YYYY-MM-DD)"),
    fecha_fin: date_type = Query(..., description="Fecha final del rango (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha final no puede ser menor que la fecha inicial",
        )

    fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
    fecha_fin_dt = datetime.combine(fecha_fin, time.max)

    result = await db.execute(
        select(Factura)
        .options(
            selectinload(Factura.sucursal),
            selectinload(Factura.moneda),
            selectinload(Factura.metodo_pago),
            selectinload(Factura.status),
            selectinload(Factura.detalles).selectinload(FacturaDetalle.producto),
        )
        .where(and_(Factura.created_at >= fecha_inicio_dt, Factura.created_at <= fecha_fin_dt))
        .order_by(Factura.created_at.desc())
    )
    facturas = result.scalars().all()
    if not facturas:
        raise HTTPException(
            status_code=404,
            detail=f"No hay facturas para el rango de fechas indicado: {fecha_inicio} - {fecha_fin}",
        )
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

        precio = item.precio_unitario if item.precio_unitario is not None else float(producto.precio)
        precio_linea = precio * item.cantidad
        if item.descuento is not None:
            descuento_linea = item.descuento
        else:
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

    descuento_total = sum(d["descuento"] for d in detalle_items_data)
    base_imponible_total = subtotal - descuento_total
    itbis_total = sum(d["itbis_aplicado"] for d in detalle_items_data)
    total_general = base_imponible_total + itbis_total

    fiscal_data = {}
    if factura.fiscal:
        fecha_venc = None
        if factura.fiscal.fecha_vencimiento_ncf:
            fecha_venc = date_type.fromisoformat(factura.fiscal.fecha_vencimiento_ncf)
        fiscal_data = {
            "ncf": factura.fiscal.ncf,
            "tipo_ncf": factura.fiscal.tipo_ncf,
            "rnc_cliente": factura.fiscal.rnc_cliente,
            "nombre_cliente_fiscal": factura.fiscal.nombre_cliente_fiscal,
            "fecha_vencimiento_ncf": fecha_venc,
        }

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
        **fiscal_data,
    )
    db.add(new_factura)
    await db.flush()

    for d_data in detalle_items_data:
        detalle = FacturaDetalle(factura_id=new_factura.id, **d_data)
        db.add(detalle)

    await db.commit()
    await db.refresh(
        new_factura,
        attribute_names=[
            "detalles",
            "sucursal",
            "moneda",
            "metodo_pago",
            "status",
        ],
    )
    for detalle in new_factura.detalles:
        await db.refresh(detalle, attribute_names=["producto"])

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
