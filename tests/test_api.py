"""Unit and integration tests for FastAPI core endpoints."""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "distributed-trace-backend"
    assert "timestamp" in data


def test_summary():
    response = client.get("/summary")
    assert response.status_code == 200
    data = response.json()
    assert "services_count" in data
    assert "traces_count" in data
    assert "active_regressions_count" in data
    assert data["services_count"] > 0


def test_services_list():
    response = client.get("/services")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "payment-service" in data
    assert "order-service" in data


def test_dependencies():
    response = client.get("/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "dependencies" in data
    assert len(data["dependencies"]) > 0
    edge = data["dependencies"][0]
    assert "source" in edge
    assert "target" in edge
    assert "call_count" in edge


def test_traces_list_and_detail():
    response = client.get("/traces")
    assert response.status_code == 200
    traces = response.json()
    assert isinstance(traces, list)
    assert len(traces) > 0

    first_tid = traces[0]["trace_id"]
    detail_resp = client.get(f"/trace/{first_tid}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["trace_id"] == first_tid
    assert len(detail["spans"]) > 0


def test_trace_not_found():
    response = client.get("/trace/non-existent-trace-id-9999")
    assert response.status_code == 404
