import pytest


@pytest.mark.asyncio
async def test_create_factura(async_client, usuario_admin):
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
    assert "data" in data
    assert "encabezado" in data["data"]
    assert "detalle" in data["data"]
    encabezado = data["data"]["encabezado"]
    assert encabezado["id_factura"] is not None
    assert encabezado["id_cliente"] == usuario_admin.id
    assert encabezado["subtotal"] > 0
    assert encabezado["descuento"] > 0
    assert encabezado["total_general"] > 0


@pytest.mark.asyncio
async def test_list_facturas(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/facturas/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
