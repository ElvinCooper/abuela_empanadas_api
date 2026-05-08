import pytest

_factura_id: int | None = None


@pytest.mark.asyncio
async def test_create_factura(async_client, usuario_admin):
    global _factura_id
    response = await async_client.post(
        "/api/v1/facturas/",
        json={
            "id_cliente": usuario_admin.id,
            "id_moneda": 1,
            "id_metodo_pago": 1,
            "porcentaje_descuento": 10.0,
            "detalle": [
                {"id_producto": 1, "cantidad": 2, "itbis": 18},
            ],
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "encabezado" in data
    assert "fiscal" in data
    assert "detalle" in data
    assert data["fiscal"]["requiere_ncf"] is False
    assert data["fiscal"]["ncf"] is None
    encabezado = data["encabezado"]
    assert encabezado["id_factura"] is not None
    assert encabezado["id_cliente"] == usuario_admin.id
    assert encabezado["subtotal"] > 0
    assert encabezado["descuento"] > 0
    assert encabezado["base_imponible"] > 0
    assert encabezado["total_itbis"] > 0
    assert encabezado["total"] > 0
    assert len(data["detalle"]) > 0
    detalle = data["detalle"][0]
    assert detalle["descripcion"] != ""
    assert detalle["precio_unitario"] > 0
    assert detalle["subtotal_linea"] > 0
    assert detalle["base_imponible"] > 0
    assert detalle["porcentaje_itbis"] >= 0
    assert detalle["itbis"] >= 0
    assert detalle["total_linea"] > 0
    _factura_id = encabezado["id_factura"]


@pytest.mark.asyncio
async def test_create_factura_with_fiscal_data(async_client, usuario_admin):
    global _factura_id
    response = await async_client.post(
        "/api/v1/facturas/",
        json={
            "id_cliente": usuario_admin.id,
            "id_moneda": 1,
            "id_metodo_pago": 1,
            "detalle": [
                {"id_producto": 1, "cantidad": 1, "itbis": 18},
            ],
            "fiscal": {
                "ncf": "E310000000001",
                "tipo_ncf": "B01",
                "rnc_cliente": "123456789",
                "nombre_cliente_fiscal": "Cliente SA",
                "fecha_vencimiento_ncf": "2026-12-31",
            },
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    fiscal = data["fiscal"]
    assert fiscal["requiere_ncf"] is True
    assert fiscal["ncf"] == "E310000000001"
    assert fiscal["tipo_ncf"] == "B01"
    assert fiscal["rnc_cliente"] == "123456789"
    assert fiscal["nombre_cliente_fiscal"] == "Cliente SA"
    assert fiscal["fecha_vencimiento_ncf"] == "2026-12-31"
    assert fiscal["rnc_emisor"] is None
    assert fiscal["razon_social_emisor"] is None
    assert fiscal["estado_fiscal"] is None
    _factura_id = data["encabezado"]["id_factura"]


@pytest.mark.asyncio
async def test_list_facturas(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/facturas/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_anular_factura(async_client, usuario_admin):
    global _factura_id
    assert _factura_id is not None
    response = await async_client.post(
        f"/api/v1/facturas/{_factura_id}/anular",
        json={"factura_id": _factura_id, "motivo": "Error en precio"},
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["factura_id"] == _factura_id
    assert data["motivo"] == "Error en precio"


@pytest.mark.asyncio
async def test_list_facturas_anuladas(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/facturas/anuladas",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
