"""Tests for Regression, Latency, and Deployment endpoints."""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_latency_metrics():
    response = client.get("/latency")
    assert response.status_code == 200
    data = response.json()
    assert "overall_percentiles" in data
    assert "p50" in data["overall_percentiles"]
    assert "by_service" in data
    assert "timeseries" in data


def test_regressions_list():
    response = client.get("/regressions")
    assert response.status_code == 200
    regressions = response.json()
    assert isinstance(regressions, list)
    assert len(regressions) > 0

    first_reg = regressions[0]
    assert "regression_id" in first_reg
    assert "severity" in first_reg


def test_regression_detail_and_evidence():
    reg_id = "REG-101"
    response = client.get(f"/regression/{reg_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["regression_id"] == reg_id

    ev_resp = client.get(f"/regression/{reg_id}/evidence")
    assert ev_resp.status_code == 200
    evidence = ev_resp.json()
    assert evidence["regression_id"] == reg_id
    assert "critical_path" in evidence
    assert "span_attribution" in evidence


def test_regression_not_found():
    response = client.get("/regression/REG-999999")
    assert response.status_code == 404


def test_deployments_list():
    response = client.get("/deployments")
    assert response.status_code == 200
    deps = response.json()
    assert isinstance(deps, list)
    assert len(deps) > 0
    assert "commit_sha" in deps[0]
