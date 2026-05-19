from datetime import date as date_type, datetime, time, timezone, timedelta
from io import BytesIO
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.styles.numbers import FORMAT_CURRENCY_USD_SIMPLE
from app.core.dependencies import get_db, get_current_user
from app.core.logging_config import get_logger
from app.models.usuario import Usuario
from app.models.factura import Factura, FacturaDetalle
from app.models.producto import Producto
from app.models.status_factura import StatusFactura
from app.models.anulacion import Anulacion
from app.schemas.factura import FacturaCreate, FacturaDataResponse
from app.schemas.anulacion import AnulacionCreate, AnulacionRead

router = APIRouter()
logger = get_logger(__name__)

ITBIS_TASA = 0.18
CATEGORIA_EMPANADAS = "Empanadas"


@router.get("/", response_model=list[FacturaDataResponse])
async def list_facturas(
    fecha_inicio: date_type = Query(..., description="Fecha inicial del rango (YYYY-MM-DD)"),
    fecha_fin: date_type = Query(..., description="Fecha final del rango (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        if fecha_fin < fecha_inicio:
            logger.error("Error listing invoices: Invalid date range")
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
            logger.warning("No invoices found for the requested date range")
            raise HTTPException(
                status_code=404,
                detail=f"No hay facturas para el rango de fechas indicado: {fecha_inicio} - {fecha_fin}",
            )
        return facturas
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing invoices: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Error retrieving invoices")


@router.post("/", response_model=FacturaDataResponse, status_code=201)
async def create_factura(
    factura: FacturaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        detalle_items_data: list[dict[str, float | int]] = []
        subtotal = 0.0

        for item in factura.detalle:
            producto_result = await db.execute(
                select(Producto)
                .options(selectinload(Producto.categoria))
                .where(Producto.id == item.id_producto)
            )
            producto = producto_result.scalar_one_or_none()
            if producto is None:
                logger.error(f"Error creating invoice: Product {item.id_producto} not found")
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto con id {item.id_producto} no encontrado",
                )

            categoria_nombre = producto.categoria.nombre if producto.categoria else ""
            es_empanada = categoria_nombre == CATEGORIA_EMPANADAS

            if es_empanada:
                stock_actual = producto.stock or 0
                if stock_actual < item.cantidad:
                    logger.error(f"Error creating invoice: Insufficient stock for {producto.nombre}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"El producto '{producto.nombre}' solo tiene {stock_actual} unidades disponibles"
                    )
                producto.stock = int(stock_actual - item.cantidad)  # type: ignore[assignment]

            precio = item.precio_unitario if item.precio_unitario is not None else float(producto.precio)  # type: ignore[arg-type]
            precio_linea = precio * item.cantidad
            if item.descuento is not None:
                descuento_linea = item.descuento
            else:
                descuento_linea = precio_linea * (factura.porcentaje_descuento / 100)
            base_imponible = precio_linea - descuento_linea
            itbis_aplicado = base_imponible * ITBIS_TASA
            total_linea = base_imponible + itbis_aplicado

            detalle_items_data.append(
                {
                    "producto_id": item.id_producto,
                    "cantidad": item.cantidad,
                    "precio_unitario": precio,
                    "descuento": descuento_linea,
                    "base_imponible": base_imponible,
                    "itbis": ITBIS_TASA * 100,
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

        offset = timezone(timedelta(hours=-4))
        ahora = datetime.now(offset)
        fecha_hora_rd = ahora.replace(tzinfo=None)

        new_factura = Factura(
            sucursal_id=current_user.sucursal_id,
            usuario_id=factura.id_cliente,
            id_status=2,
            id_moneda=factura.id_moneda,
            id_metodo_pago=factura.id_metodo_pago,
            subtotal=subtotal,
            porcentaje_descuento=factura.porcentaje_descuento,
            descuento=descuento_total,
            itbis=itbis_total,
            total_general=total_general,
            created_at=fecha_hora_rd,
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

        return new_factura
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating invoice: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Error creating invoice")


@router.get("/anuladas", response_model=list[AnulacionRead])
async def listar_facturas_anuladas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        result = await db.execute(select(Anulacion))
        anulaciones = result.scalars().all()
        if not anulaciones:
            logger.warning("No cancelled invoices found")
        return anulaciones
    except Exception as e:
        logger.error(f"Error listing cancelled invoices: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Error retrieving cancelled invoices")


@router.post("/{factura_id}/anular", response_model=AnulacionRead, status_code=201)
async def anular_factura(
    factura_id: int,
    anulacion: AnulacionCreate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        anulada_result = await db.execute(
            select(StatusFactura).where(StatusFactura.nombre == "anulada")
        )
        status_anulada = anulada_result.scalar_one()

        factura_result = await db.execute(
            select(Factura)
            .options(selectinload(Factura.detalles).selectinload(FacturaDetalle.producto).selectinload(Producto.categoria))
            .where(Factura.id == factura_id)
        )
        factura = factura_result.scalar_one_or_none()

        if factura is None:
            logger.error(f"Error cancelling invoice: Invoice {factura_id} not found")
            raise HTTPException(status_code=404, detail="Factura no encontrada")

        for detalle in factura.detalles:
            if detalle.producto and detalle.producto.categoria:
                if detalle.producto.categoria.nombre == CATEGORIA_EMPANADAS:
                    stock_actual = detalle.producto.stock or 0
                    detalle.producto.stock = stock_actual + detalle.cantidad

        factura.id_status = status_anulada.id

        new_anulacion = Anulacion(factura_id=factura_id, motivo=anulacion.motivo)
        db.add(new_anulacion)
        await db.commit()
        await db.refresh(new_anulacion)
        return new_anulacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling invoice: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Error cancelling invoice")


@router.get("/exportar")
async def exportar_facturas_excel(
    fecha: date_type = Query(..., description="Fecha a exportar (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        fecha_inicio_dt = datetime.combine(fecha, time.min)
        fecha_fin_dt = datetime.combine(fecha, time.max)

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
            .order_by(Factura.created_at.asc())
        )
        facturas = result.scalars().all()

        if not facturas:
            raise HTTPException(
                status_code=404,
                detail=f"No hay facturas para la fecha indicated: {fecha}",
            )

        wb = Workbook()
        ws_resumen = wb.active
        ws_resumen.title = "Resumen Facturas"
        ws_detalle = wb.create_sheet("Detalle Productos")

        header_font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        fecha_formateada = fecha.strftime("%d/%m/%Y")
        ws_resumen.merge_cells("A1:I1")
        ws_resumen["A1"] = f"RESUMEN DE VENTAS DEL DÍA - Abuela Empanadas\n{fecha_formateada}"
        ws_resumen["A1"].font = header_font
        ws_resumen["A1"].fill = header_fill
        ws_resumen["A1"].alignment = header_alignment
        ws_resumen.row_dimensions[1].height = 35

        ws_detalle.merge_cells("A1:I1")
        ws_detalle["A1"] = f"RESUMEN DE VENTAS DEL DÍA - Abuela Empanadas\n{fecha_formateada}"
        ws_detalle["A1"].font = header_font
        ws_detalle["A1"].fill = header_fill
        ws_detalle["A1"].alignment = header_alignment
        ws_detalle.row_dimensions[1].height = 35

        cols_resumen = ["Fecha", "Sucursal", "Método Pago", "Estado", "Subtotal", "Descuento", "ITBIS", "Total"]
        cols_detalle = ["ID Factura", "Producto", "Cantidad", "Precio Unit.", "Descuento", "Base Imponible", "ITBIS", "Sub-Total"]

        for col_idx, col_name in enumerate(cols_resumen, start=1):
            cell = ws_resumen.cell(row=3, column=col_idx, value=col_name)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        for col_idx, col_name in enumerate(cols_detalle, start=1):
            cell = ws_detalle.cell(row=3, column=col_idx, value=col_name)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        total_subtotal = 0.0
        total_descuento = 0.0
        total_itbis = 0.0
        total_general = 0.0
        total_precio = 0.0
        total_base = 0.0
        total_linea = 0.0
        row_num = 4
        detalle_row = 4

        for idx, factura in enumerate(facturas, start=1):
            fecha_str = factura.created_at.strftime("%Y-%m-%d %H:%M") if factura.created_at else ""
            sucursal_nom = getattr(getattr(factura, 'sucursal', None), 'nombre', '') or ""
            metodo_pago_nom = getattr(getattr(factura, 'metodo_pago', None), 'nombre', '') or ""
            status_nom = getattr(getattr(factura, 'status', None), 'nombre', '') or ""

            ws_resumen.cell(row=row_num, column=1, value=fecha_str)
            ws_resumen.cell(row=row_num, column=2, value=sucursal_nom)
            ws_resumen.cell(row=row_num, column=3, value=metodo_pago_nom)
            ws_resumen.cell(row=row_num, column=4, value=status_nom)

            cell_subtotal = ws_resumen.cell(row=row_num, column=5, value=float(factura.subtotal or 0))
            cell_subtotal.number_format = FORMAT_CURRENCY_USD_SIMPLE

            cell_descuento = ws_resumen.cell(row=row_num, column=6, value=float(factura.descuento or 0))
            cell_descuento.number_format = FORMAT_CURRENCY_USD_SIMPLE

            cell_itbis = ws_resumen.cell(row=row_num, column=7, value=float(factura.itbis or 0))
            cell_itbis.number_format = FORMAT_CURRENCY_USD_SIMPLE

            cell_total = ws_resumen.cell(row=row_num, column=8, value=float(factura.total_general or 0))
            cell_total.number_format = FORMAT_CURRENCY_USD_SIMPLE

            total_subtotal += float(factura.subtotal or 0)  # type: ignore[assignment]
            total_descuento += float(factura.descuento or 0)  # type: ignore[assignment]
            total_itbis += float(factura.itbis or 0)  # type: ignore[assignment]
            total_general += float(factura.total_general or 0)  # type: ignore[assignment]
            row_num += 1

            for detalle in factura.detalles:
                producto_nom = getattr(getattr(detalle, 'producto', None), 'nombre', '') or ""
                ws_detalle.cell(row=detalle_row, column=1, value=factura.id)
                ws_detalle.cell(row=detalle_row, column=2, value=producto_nom)
                ws_detalle.cell(row=detalle_row, column=3, value=detalle.cantidad)

                cell_precio = ws_detalle.cell(row=detalle_row, column=4, value=float(detalle.precio_unitario or 0))
                cell_precio.number_format = FORMAT_CURRENCY_USD_SIMPLE

                cell_desc = ws_detalle.cell(row=detalle_row, column=5, value=float(detalle.descuento or 0))
                cell_desc.number_format = FORMAT_CURRENCY_USD_SIMPLE

                cell_base = ws_detalle.cell(row=detalle_row, column=6, value=float(detalle.base_imponible or 0))
                cell_base.number_format = FORMAT_CURRENCY_USD_SIMPLE

                cell_itbis = ws_detalle.cell(row=detalle_row, column=7, value=float(detalle.itbis_aplicado or 0))
                cell_itbis.number_format = FORMAT_CURRENCY_USD_SIMPLE

                cell_subtotal = ws_detalle.cell(row=detalle_row, column=8, value=float(detalle.total_linea or 0))
                cell_subtotal.number_format = FORMAT_CURRENCY_USD_SIMPLE

                total_precio += float(detalle.precio_unitario or 0) * detalle.cantidad
                total_descuento += float(detalle.descuento or 0)
                total_base += float(detalle.base_imponible or 0)
                total_itbis += float(detalle.itbis_aplicado or 0)
                total_linea += float(detalle.total_linea or 0)

                detalle_row += 1

        total_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
        total_fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid")

        cell_tot = ws_resumen.cell(row=row_num, column=4, value="TOTALES:")
        cell_tot.font = total_font
        cell_tot.fill = total_fill

        cell_sub = ws_resumen.cell(row=row_num, column=5, value=total_subtotal)
        cell_sub.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_sub.font = total_font
        cell_sub.fill = total_fill

        cell_desc = ws_resumen.cell(row=row_num, column=6, value=total_descuento)
        cell_desc.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_desc.font = total_font
        cell_desc.fill = total_fill

        cell_itbis = ws_resumen.cell(row=row_num, column=7, value=total_itbis)
        cell_itbis.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_itbis.font = total_font
        cell_itbis.fill = total_fill

        cell_total = ws_resumen.cell(row=row_num, column=8, value=total_general)
        cell_total.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_total.font = total_font
        cell_total.fill = total_fill

        cell_total_det = ws_detalle.cell(row=detalle_row, column=2, value="TOTALES:")
        cell_total_det.font = total_font
        cell_total_det.fill = total_fill

        cell_precio_det = ws_detalle.cell(row=detalle_row, column=4, value=total_precio)
        cell_precio_det.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_precio_det.font = total_font
        cell_precio_det.fill = total_fill

        cell_desc_det = ws_detalle.cell(row=detalle_row, column=5, value=total_descuento)
        cell_desc_det.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_desc_det.font = total_font
        cell_desc_det.fill = total_fill

        cell_base_det = ws_detalle.cell(row=detalle_row, column=6, value=total_base)
        cell_base_det.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_base_det.font = total_font
        cell_base_det.fill = total_fill

        cell_itbis_det = ws_detalle.cell(row=detalle_row, column=7, value=total_itbis)
        cell_itbis_det.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_itbis_det.font = total_font
        cell_itbis_det.fill = total_fill

        cell_linea_det = ws_detalle.cell(row=detalle_row, column=8, value=total_linea)
        cell_linea_det.number_format = FORMAT_CURRENCY_USD_SIMPLE
        cell_linea_det.font = total_font
        cell_linea_det.fill = total_fill

        from openpyxl.cell import Cell

        for ws in [ws_resumen, ws_detalle]:
            for col in ws.iter_cols():
                first_cell = next((c for c in col if isinstance(c, Cell)), None)
                if not first_cell:
                    continue
                column = first_cell.column_letter
                max_length = 0
                for cell in col:
                    if isinstance(cell, Cell) and cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                if max_length > 0:
                    ws.column_dimensions[column].width = max_length + 2

        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)

        fecha_filename = fecha.strftime("%Y-%m-%d")
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=facturas_{fecha_filename}.xlsx"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting invoices: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error exporting invoices")
