from fastapi.testclient import TestClient

from app.main import app


def test_root_and_health_endpoints():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    payload = client.get("/").json()
    assert payload["service"] == "Order Sync API"
    assert payload["status"] == "ok"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


def test_api_clients_endpoint_returns_expected_shape():
    client = TestClient(app)
    response = client.get("/api/clients")
    assert response.status_code == 200
    payload = response.json()

    assert set(payload.keys()) == {"clients", "stats"}
    assert isinstance(payload["clients"], list)
    assert isinstance(payload["stats"], dict)
    assert set(payload["stats"].keys()) == {"received", "unique", "duplicates_merged", "invalid_dropped"}
    for item in payload["clients"]:
        assert set(item.keys()) == {"name", "phone", "email", "amount"}
        assert item["phone"].startswith("+")
        assert len(item["phone"]) == 12

    phones = [client_item["phone"] for client_item in payload["clients"]]
    assert phones == sorted(phones)
