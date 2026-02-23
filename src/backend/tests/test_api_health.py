from __future__ import annotations

from app.api.v1.endpoints.health import read_health


def test_health_endpoint_contract() -> None:
    response = read_health()

    assert response.status == "ok"
    assert response.service
    assert response.version
