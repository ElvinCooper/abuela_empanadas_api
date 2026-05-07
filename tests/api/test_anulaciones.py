import pytest


@pytest.mark.asyncio
async def test_anular_factura(async_client, usuario_admin):
    factura_response = await async_client.post(
        "/api/v1/facturas/",
        json={
            "id_cliente": usuario_admin.id,
            "id_moneda": 1,
            "id_metodo_pago": 1,
            "porcentaje_descuento": 0,
            "detalle": [
                {"id_producto": 1, "cantidad": 5, "itbis": 0},
            ],
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert factura_response.status_code == 201
    factura_id = factura_response.json()["encabezado"]["id_factura"]

    response = await async_client.post(
        f"/api/v1/facturas/{factura_id}/anular",
        json={"factura_id": factura_id, "motivo": "Error en precio"},
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["factura_id"] == factura_id
    assert data["motivo"] == "Error en precio"


@pytest.mark.asyncio
async def test_list_facturas_anuladas(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/facturas/anuladas",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
