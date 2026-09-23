"""Tests for Integration Layer and LangGraph RCA Agent."""
from fastapi.testclient import TestClient
from api.main import app
from src.integration import integration_client
from src.agent import run_rca_workflow

client = TestClient(app)


def test_integration_client_methods():
    services = integration_client.services()
    assert isinstance(services, list)
    assert len(services) > 0

    deps = integration_client.dependencies()
    assert isinstance(deps, list)

    traces = integration_client.traces()
    assert len(traces) > 0

    regs = integration_client.regressions()
    assert len(regs) > 0

    deployments = integration_client.deployments()
    assert len(deployments) > 0


def test_rca_workflow_success():
    reg_id = "REG-101"
    rca = run_rca_workflow(reg_id)

    assert rca["regression_id"] == reg_id
    assert rca["evidence_validated"] is True
    assert rca["confidence_score"] > 50.0
    assert "payment-service" in rca["culprit_service"]
    assert len(rca["workflow_steps"]) >= 6
    assert len(rca["remediation_recommendations"]) > 0


def test_rca_workflow_insufficient_evidence():
    reg_id = "NON-EXISTENT-REGRESSION"
    rca = run_rca_workflow(reg_id)

    assert rca["evidence_validated"] is False
    assert "Insufficient evidence" in rca["hypothesis"]
    assert rca["confidence_score"] == 0.0


def test_api_rca_endpoints():
    reg_id = "REG-101"

    # GET /root-cause/{regression_id}
    res_get = client.get(f"/root-cause/{reg_id}")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["regression_id"] == reg_id
    assert data_get["evidence_validated"] is True

    # POST /analyze
    res_post = client.post("/analyze", json={"regression_id": reg_id})
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["regression_id"] == reg_id
    assert data_post["evidence_validated"] is True
