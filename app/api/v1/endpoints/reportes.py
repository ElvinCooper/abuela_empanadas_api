from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Date, select, func, and_
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.sucursal import Sucursal
from app.models.factura import Factura, FacturaDetalle
from app.models.producto import Producto
from app.models.metodo_pago import MetodoPago
from app.models.egreso import Egreso
from app.utils.pdf_generator import (
    generar_recibo_factura,
    generar_reporte_ventas_termico,
    generar_reporte_estado_termico,
)

router = APIRouter()


@router.get("/")
async def generate_reporte(
    desde: date = Query(...),
    hasta: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if hasta < desde:
        raise HTTPException(
            status_code=400,
            detail="la fecha_fin no puede ser menor a la fecha_inicio"
        )

    facturas_result = await db.execute(
        select(func.sum(Factura.total_general)).where(
            and_(
                Factura.id_status != 3,
                Factura.created_at.cast(Date) >= desde,
                Factura.created_at.cast(Date) <= hasta,
            )
        )
    )
    total_ventas = float(facturas_result.scalar() or 0)

    gastos_result = await db.execute(
        select(func.sum(Egreso.monto)).where(
            and_(
                Egreso.created_at.cast(Date) >= desde,
                Egreso.created_at.cast(Date) <= hasta,
            )
        )
    )
    total_gastos = float(gastos_result.scalar() or 0)
    utilidad = total_ventas - total_gastos

    if total_ventas == 0 and total_gastos == 0:
        raise HTTPException(
            status_code=404,
            detail=f"no existen datos para el rango de fechas {desde.strftime('%d-%m-%Y')} hasta {hasta.strftime('%d-%m-%Y')}"
        )

    offset = timezone(timedelta(hours=-4))
    ahora = datetime.now(offset)
    ahora_str = ahora.strftime("%d-%m-%Y %H:%M")
    fecha_filename = ahora.strftime("%Y%m%d")

    sucursal_result = await db.execute(
        select(Sucursal).where(Sucursal.id == current_user.sucursal_id)
    )
    sucursal = sucursal_result.scalar_one_or_none()

    datos_reporte = {
        "empresa": sucursal.nombre if sucursal else "Abuela Empanadas",
        "direccion": sucursal.direccion if sucursal else "",
        "telefono": sucursal.telefono if sucursal else "",
        "rnc": "",
        "desde": desde.strftime("%d-%m-%Y"),
        "hasta": hasta.strftime("%d-%m-%Y"),
        "fechas_iguales": desde == hasta,
        "fecha_impresion": ahora_str,
        "usuario": current_user.nombre,
        "total_ventas": total_ventas,
        "total_gastos": total_gastos,
        "utilidad": utilidad,
    }

    pdf_buffer = generar_reporte_estado_termico(datos_reporte)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_estado_{fecha_filename}.pdf"
        },
    )


@router.get("/recibo/{factura_id}")
async def generar_recibo(
    factura_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Factura)
        .options(
            selectinload(Factura.sucursal),
            selectinload(Factura.moneda),
            selectinload(Factura.metodo_pago),
            selectinload(Factura.usuario),
            selectinload(Factura.detalles).selectinload(FacturaDetalle.producto),
        )
        .where(Factura.id == factura_id)
    )
    factura = result.scalar_one_or_none()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    fecha_str = factura.created_at.strftime("%d-%m-%Y %H:%M") if factura.created_at else ""  # type: ignore[truthy-col]
    items = []
    for d in factura.detalles:
        items.append({
            "descripcion": d.producto.nombre if d.producto else "",
            "cantidad": d.cantidad,
            "precio_unitario": float(d.precio_unitario),
            "total": float(d.total_linea),
        })

    base_imponible = float(factura.subtotal - factura.descuento)  # type: ignore[arg-type]

    datos_recibo = {
        "empresa": factura.sucursal.nombre if factura.sucursal else "",
        "direccion": factura.sucursal.direccion if factura.sucursal else "",
        "telefono": factura.sucursal.telefono if factura.sucursal else "",
        "rnc": factura.rnc_emisor or "",
        "factura_id": factura.id,
        "cliente": factura.usuario.nombre if factura.usuario else "",
        "atendido_por": current_user.nombre,
        "fecha": fecha_str,
        "metodo_pago": factura.metodo_pago.nombre if factura.metodo_pago else "",
        "items": items,
        "subtotal": float(factura.subtotal),  # type: ignore[arg-type]
        "porcentaje_descuento": float(factura.porcentaje_descuento),  # type: ignore[arg-type]
        "descuento": float(factura.descuento),  # type: ignore[arg-type]
        "base_imponible": base_imponible,
        "itbis": float(factura.itbis),  # type: ignore[arg-type]
        "total": float(factura.total_general),  # type: ignore[arg-type]
    }

    pdf_buffer = generar_recibo_factura(datos_recibo)
    fecha_filename = fecha_str[:10].replace("-", "") if fecha_str else ""
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=recibo_{factura_id}_{fecha_filename}.pdf"
        },
    )


@router.get("/ventas-termico")
async def generar_reporte_ventas(
    desde: date = Query(...),
    hasta: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if hasta < desde:
        raise HTTPException(
            status_code=400,
            detail="la fecha_fin no puede ser menor a la fecha_inicio"
        )

    offset = timezone(timedelta(hours=-4))
    ahora = datetime.now(offset)
    ahora_str = ahora.strftime("%d-%m-%Y %H:%M")
    fecha_filename = ahora.strftime("%Y%m%d")

    sucursal_result = await db.execute(
        select(Sucursal).where(Sucursal.id == current_user.sucursal_id)
    )
    sucursal = sucursal_result.scalar_one_or_none()

    productos_rows = await db.execute(
        select(
            Producto.nombre,
            func.sum(FacturaDetalle.total_linea),
        )
        .join(FacturaDetalle, FacturaDetalle.producto_id == Producto.id)
        .join(Factura, Factura.id == FacturaDetalle.factura_id)
        .where(
            and_(
                Factura.id_status != 3,
                Factura.created_at.cast(Date) >= desde,
                Factura.created_at.cast(Date) <= hasta,
            )
        )
        .group_by(Producto.nombre)
        .order_by(func.sum(FacturaDetalle.total_linea).desc())
    )
    items = [
        {"descripcion": row[0], "valor": float(row[1] or 0)}
        for row in productos_rows
    ]

    pagos_rows = await db.execute(
        select(
            MetodoPago.nombre,
            func.sum(Factura.total_general),
        )
        .join(Factura, Factura.id_metodo_pago == MetodoPago.id)
        .where(
            and_(
                Factura.id_status != 3,
                Factura.created_at.cast(Date) >= desde,
                Factura.created_at.cast(Date) <= hasta,
            )
        )
        .group_by(MetodoPago.nombre)
    )
    pagos = [
        {"tipo": row[0], "valor": float(row[1] or 0)}
        for row in pagos_rows
    ]

    total = sum(item["valor"] for item in items)

    if total == 0:
        raise HTTPException(
            status_code=404,
            detail=f"no existen datos para el rango de fechas {desde.strftime('%d-%m-%Y')} hasta {hasta.strftime('%d-%m-%Y')}"
        )

    datos_reporte = {
        "empresa": sucursal.nombre if sucursal else "Abuela Empanadas",
        "direccion": sucursal.direccion if sucursal else "",
        "telefono": sucursal.telefono if sucursal else "",
        "rnc": "",
        "desde": desde.strftime("%d-%m-%Y"),
        "hasta": hasta.strftime("%d-%m-%Y"),
        "fechas_iguales": desde == hasta,
        "fecha_impresion": ahora_str,
        "usuario": current_user.nombre,
        "items": items,
        "total": total,
        "pagos": pagos,
    }

    pdf_buffer = generar_reporte_ventas_termico(datos_reporte)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_ventas_{fecha_filename}.pdf"
        },
    )
