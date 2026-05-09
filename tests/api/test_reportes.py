from datetime import date, timedelta

import pytest


@pytest.mark.asyncio
async def test_get_reportes_pdf(async_client, usuario_admin):
    today = date.today()

    response = await async_client.post(
        "/api/v1/facturas/",
        json={
            "id_cliente": usuario_admin.id,
            "id_moneda": 1,
            "id_metodo_pago": 1,
            "porcentaje_descuento": 0,
            "detalle": [
                {"id_producto": 1, "cantidad": 2, "itbis": 18},
            ],
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201
    _factura_id = response.json()["encabezado"]["id_factura"]

    response = await async_client.post(
        "/api/v1/gastos/",
        json={
            "sucursal_id": 1,
            "descripcion": "Gasto test",
            "monto": 100,
        },
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 201

    response = await async_client.get(
        f"/api/v1/reportes/?desde={today}&hasta={today}",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

    response = await async_client.get(
        f"/api/v1/reportes/recibo/{_factura_id}",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

    response = await async_client.get(
        f"/api/v1/reportes/ventas-termico?desde={today}&hasta={today}",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_reportes_without_authorization(async_client):
    response = await async_client.get(
        "/api/v1/reportes/?desde=2026-01-01&hasta=2026-12-31"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_recibo_not_found(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/reportes/recibo/99999",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_reportes_empty_range(async_client, usuario_admin):
    yesterday = date.today() - timedelta(days=365)
    before = yesterday - timedelta(days=10)
    response = await async_client.get(
        f"/api/v1/reportes/?desde={before}&hasta={yesterday}",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_reportes_missing_dates(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/reportes/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 422
