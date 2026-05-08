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
    assert "detalle" in data
    encabezado = data["encabezado"]
    assert encabezado["id_factura"] is not None
    assert encabezado["id_cliente"] == usuario_admin.id
    assert encabezado["subtotal"] > 0
    assert encabezado["descuento"] > 0
    assert encabezado["total_general"] > 0
    _factura_id = encabezado["id_factura"]


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
