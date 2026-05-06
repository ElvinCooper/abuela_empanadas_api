import pytest


@pytest.mark.asyncio
async def test_get_reportes_with_authorization(async_client, usuario_admin):
    response = await async_client.get(
        "/api/v1/reportes/",
        headers={"Authorization": f"Bearer {usuario_admin.token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_ventas" in data
    assert "total_gastos" in data
    assert "utilidad" in data
    assert isinstance(data["total_ventas"], (int, float))
    assert isinstance(data["total_gastos"], (int, float))
    assert isinstance(data["utilidad"], (int, float))
    assert data["utilidad"] == data["total_ventas"] - data["total_gastos"]
