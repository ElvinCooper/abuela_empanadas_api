from datetime import date as date_type, datetime, time, timezone, timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.core.logging_config import get_logger
from app.models.usuario import Usuario
from app.models.factura import Factura, FacturaDetalle
from app.models.producto import Producto
from app.models.categoria import Categoria
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
