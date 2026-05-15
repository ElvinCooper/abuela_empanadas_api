from io import BytesIO
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode


def generar_recibo_factura(datos: dict) -> BytesIO:
    buffer = BytesIO()
    width = 70 * mm
    height = 200 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))
    y = height - 15
    page_number = 1

    def linea():
        nonlocal y
        y -= 5
        c.setFont("Courier", 8)
        c.drawString(5, y, "-" * 42)

    def espacio(px=8):
        nonlocal y
        y -= px

    def check_page_overflow(min_y=20):
        nonlocal y, page_number
        if y < min_y:
            c.showPage()
            y = height - 10
            page_number += 1
            c.setFont("Courier", 8)
            c.drawString(5, y, f"Pag. {page_number}")

    def texto_centrado(txt, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawCentredString(width / 2, y, txt)

    def texto_izq_der(izq, der, size=9, bold=False, max_izq=25):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        if len(izq) > max_izq:
            izq = izq[: max_izq - 2] + ".."
        c.drawString(5, y, izq)
        c.drawRightString(width - 5, y, der)

    texto_centrado(datos.get("empresa", "EMPRESA"), 10, True)
    espacio(8)
    if datos.get("direccion"):
        texto_centrado(datos["direccion"], 8)
        espacio(8)
    if datos.get("telefono"):
        texto_centrado(f"Tel: {datos['telefono']}", 8)
        espacio(8)
    if datos.get("rnc"):
        texto_centrado(f"RNC: {datos['rnc']}", 8)
        espacio(8)

    linea()
    espacio(8)
    texto_centrado("FACTURA", 10, True)
    espacio(8)
    texto_centrado(datos.get("fecha", ""), 8)
    espacio(8)
    texto_centrado(datos.get("metodo_pago", ""), 9, True)
    linea()

    espacio(8)
    c.setFont("Courier", 9)
    c.drawString(5, y, f"No. Factura: {datos.get('factura_id', '')}")
    espacio(10)
    cliente = datos.get("cliente", "")
    if len(cliente) > 25:
        cliente = cliente[:23] + ".."
    c.drawString(5, y, f"Cliente: {cliente}")
    espacio(10)
    c.drawString(5, y, f"Atendido por: {datos.get('atendido_por', '')}")

    espacio(14)
    texto_centrado("DETALLE", 9, True)
    espacio(12)
    texto_izq_der("Descripcion    CANT     ITBIS", "Total", 8, True, 30)
    espacio(6)
    linea()

    items = datos.get("items", [])
    total_itbis_items = sum(item.get("itbis", 0) for item in items)

    for item in items:
        check_page_overflow(30)
        espacio(10)
        c.setFont("Courier", 8)
        desc = item.get("descripcion", "")
        cant = item.get("cantidad", 0)
        itbis_item = item.get("itbis", 0)
        total_item = item.get("total", 0)

        max_desc = 15
        if len(desc) <= max_desc:
            linea_texto = f"{desc:<{max_desc}} {cant}        {itbis_item:,.2f}"
            c.drawString(5, y, linea_texto)
            c.drawRightString(width - 5, y, f"{total_item:,.2f}")
        else:
            primera_parte = desc[:max_desc]
            resto = desc[max_desc:]
            c.drawString(5, y, primera_parte)
            c.drawRightString(width - 5, y, f"{total_item:,.2f}")
            espacio(10)
            c.drawString(5, y, f"{resto:<{max_desc}} {cant}        {itbis_item:,.2f}")

    espacio(6)
    c.setFont("Courier-Bold", 8)
    # c.drawRightString(width - 85, y, "TOTALES:")
    
    linea()
    espacio(8)
    texto_izq_der("Subtotal:", f"{datos.get('subtotal', 0):,.2f}", 9)
    espacio(8)
    # c.drawRightString(width - 5, y, f"{total_itbis_items:,.2f}")
    if datos.get("descuento", 0) > 0:
        texto_izq_der(f"Descuento ({datos.get('porcentaje_descuento', 0):.0f}%):", f"-{datos['descuento']:,.2f}", 9)
        espacio(8)
    texto_izq_der("ITBIS:", f"{datos.get('itbis', 0):,.2f}", 9)
    espacio(6)
    linea()
    espacio(8)
    texto_izq_der("TOTAL GENERAL:", f"{datos.get('total', 0):,.2f}", 10, True)
    espacio(16)
    texto_centrado("Gracias por su compra!", 8)
    espacio(8)
    texto_centrado("Abuela Empanadas", 8)
    espacio(10)

    qr = qrcode.QRCode(box_size=3, border=0)
    qr.add_data("https://www.instagram.com/abuelaempanadas/")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_width = 20 * mm
    qr_x = (width - qr_width) / 2
    c.drawImage(ImageReader(qr_buffer), qr_x, y - qr_width, width=qr_width, height=qr_width)
    espacio(2)

    c.save()
    buffer.seek(0)
    return buffer


def generar_reporte_ventas_termico(datos: dict) -> BytesIO:
    buffer = BytesIO()
    width = 70 * mm
    height = 180 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))
    y = height - 10
    page_number = 1

    def linea():
        nonlocal y
        y -= 5
        c.setFont("Courier", 8)
        c.drawString(5, y, "-" * 42)

    def espacio(px=8):
        nonlocal y
        y -= px

    def check_page_overflow(min_y=20):
        nonlocal y, page_number
        if y < min_y:
            c.showPage()
            y = height - 10
            page_number += 1
            c.setFont("Courier", 8)
            c.drawString(5, y, f"Pag. {page_number}")

    def texto_centrado(txt, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawCentredString(width / 2, y, txt)

    def texto_izq_der(izq, der, size=9, bold=False, max_izq=30):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        if len(izq) > max_izq:
            izq = izq[: max_izq - 2] + ".."
        c.drawString(5, y, izq)
        c.drawRightString(width - 5, y, der)

    texto_centrado(datos.get("empresa", "EMPRESA"), 10, True)
    espacio(8)
    texto_centrado(datos.get("direccion", ""), 8)
    espacio(8)
    texto_centrado(f"Tel: {datos.get('telefono', '')}", 8)
    espacio(8)
    if datos.get("rnc"):
        texto_centrado(f"RNC: {datos['rnc']}", 8)
        espacio(10)

    if datos.get("fechas_iguales"):
        texto_centrado(f"Fecha: {datos.get('desde', '')}", 8)
    else:
        texto_centrado(f"Desde: {datos.get('desde', '')}  Hasta: {datos.get('hasta', '')}", 8)
    espacio(8)
    texto_centrado(f"Impreso por: {datos.get('usuario', '')}", 8)

    linea()
    linea()
    espacio(6)
    c.setFont("Courier", 8)
    c.drawString(5, y, "Pag. 1 de 1")

    espacio(10)
    texto_centrado("RESUMEN DE VENTAS", 9, True)

    espacio(6)
    linea()
    espacio(6)
    texto_izq_der("PRODUCTO", "Valor", 9, True)
    espacio(6)
    linea()

    for item in datos.get("items", []):
        check_page_overflow(30)
        espacio(10)
        texto_izq_der(f"{item.get('producto', '')} (x{item.get('cantidad', 0)})", f"{item.get('valor', 0):,.2f}")

    espacio(10)
    linea()
    espacio(10)
    texto_izq_der("Total Gral:", f"{datos.get('total', 0):,.2f}", 10, True)

    if datos.get("pagos"):
        espacio(10)
        linea()
        espacio(8)
        texto_centrado("RESUMEN DE PAGOS", 9, True)
        espacio(6)
        linea()
        for metodo in datos["pagos"]:
            check_page_overflow(20)
            espacio(10)
            texto_izq_der(metodo.get("tipo", ""), f"{metodo.get('valor', 0):,.2f}")
        espacio(6)
        linea()

    c.save()
    buffer.seek(0)
    return buffer


def generar_reporte_estado_termico(datos: dict) -> BytesIO:
    buffer = BytesIO()
    width = 70 * mm
    height = 120 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))
    y = height - 15

    def espacio(px=8):
        nonlocal y
        y -= px

    def texto_centrado(txt, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawCentredString(width / 2, y, txt)

    def texto_izq_der(izq, der, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawString(5, y, izq)
        c.drawRightString(width - 5, y, der)

    def linea():
        nonlocal y
        y -= 5
        c.setFont("Courier", 8)
        c.drawString(5, y, "-" * 42)

    texto_centrado(datos.get("empresa", "EMPRESA"), 10, True)
    espacio(8)
    if datos.get("direccion"):
        texto_centrado(datos["direccion"], 8)
        espacio(8)
    if datos.get("telefono"):
        texto_centrado(f"Tel: {datos['telefono']}", 8)
        espacio(8)
    if datos.get("rnc"):
        texto_centrado(f"RNC: {datos['rnc']}", 8)
        espacio(8)
    if datos.get("fechas_iguales"):
        texto_centrado(f"Fecha: {datos.get('desde', '')}", 8)
    else:
        texto_centrado(f"Desde: {datos.get('desde', '')}  Hasta: {datos.get('hasta', '')}", 8)
    espacio(8)
    texto_centrado(f"Impreso por: {datos.get('usuario', '')}", 8)
    linea()
    linea()
    espacio(10)
    texto_centrado("ESTADO DE RESULTADOS", 9, True)
    espacio(6)
    linea()
    espacio(8)
    c.setFont("Courier", 9)
    c.drawString(5, y, "INGRESOS")
    espacio(8)
    texto_izq_der("Total Ventas:", f"{datos.get('total_ventas', 0):,.2f}", 9, True)
    espacio(8)
    c.drawString(5, y, "EGRESOS")
    espacio(8)
    texto_izq_der("Total Gastos:", f"{datos.get('total_gastos', 0):,.2f}", 9, True)
    linea()
    espacio(8)
    texto_izq_der("UTILIDAD:", f"{datos.get('utilidad', 0):,.2f}", 10, True)
    linea()
    espacio(16)
    texto_centrado("Abuela Empanadas", 8)

    c.save()
    buffer.seek(0)
    return buffer
