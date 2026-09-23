"""FastAPI routes for Distributed Trace & RCA Platform."""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime, timezone

from api.schemas import (
    HealthResponse,
    SummaryResponse,
    TopologyResponse,
    TraceSummary,
    TraceDetail,
    LatencyResponse,
    RegressionItem,
    DeploymentItem,
    EvidenceModel,
    RCAResponse,
    AnalyzeRequest,
)
from src.integration import integration_client
from src.agent import run_rca_workflow

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health():
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "ok",
        "service": "distributed-trace-backend",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/summary", response_model=SummaryResponse, tags=["Overview"])
def get_summary():
    """Aggregated system metrics summary."""
    services = integration_client.services()
    traces = integration_client.traces()
    regressions = integration_client.regressions()
    deployments = integration_client.deployments()
    latency_data = integration_client.latency()

    p50 = latency_data.get("overall_percentiles", {}).get("p50", 0.0)
    active_reg_count = sum(1 for r in regressions if r.get("status") == "ACTIVE")

    return {
        "services_count": len(services),
        "traces_count": len(traces),
        "active_regressions_count": active_reg_count,
        "recent_deployments_count": len(deployments),
        "avg_latency_ms": p50,
        "system_status": "DEGRADED" if active_reg_count > 0 else "HEALTHY"
    }


@router.get("/services", response_model=List[str], tags=["Topology"])
def get_services():
    """Returns list of all active microservices."""
    return integration_client.services()


@router.get("/dependencies", tags=["Topology"])
def get_dependencies():
    """Returns microservice topology and communication dependency edges."""
    return {
        "services": integration_client.services(),
        "dependencies": integration_client.dependencies()
    }


@router.get("/traces", response_model=List[TraceSummary], tags=["Traces"])
def get_traces():
    """Returns recent traces list."""
    traces = integration_client.traces()
    summaries = []
    for t in traces:
        summaries.append({
            "trace_id": t["trace_id"],
            "root_service": t["root_service"],
            "root_operation": t["root_operation"],
            "timestamp": t["timestamp"],
            "duration_ms": t["duration_ms"],
            "span_count": t["span_count"],
            "has_error": t["has_error"],
            "status_code": t.get("status_code", 200)
        })
    return summaries


@router.get("/trace/{trace_id}", response_model=TraceDetail, tags=["Traces"])
def get_trace_detail(trace_id: str):
    """Retrieves full trace details, span waterfall data, and critical path."""
    trace_data = integration_client.trace(trace_id)
    if not trace_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found."
        )
    return trace_data


@router.get("/latency", response_model=LatencyResponse, tags=["Analytics"])
def get_latency():
    """Retrieves latency percentiles, per-service metrics, timeseries, and distribution."""
    return integration_client.latency()


@router.get("/regressions", response_model=List[RegressionItem], tags=["Regressions"])
def get_regressions():
    """Returns all detected performance and latency regressions."""
    return integration_client.regressions()


@router.get("/regression/{regression_id}", response_model=RegressionItem, tags=["Regressions"])
def get_regression_detail(regression_id: str):
    """Retrieves specific regression details."""
    reg = integration_client.regression(regression_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regression with ID '{regression_id}' not found."
        )
    return reg


@router.get("/regression/{regression_id}/evidence", response_model=EvidenceModel, tags=["Regressions"])
def get_regression_evidence(regression_id: str):
    """Retrieves the Member 2 evidence bundle for a regression."""
    ev = integration_client.evidence(regression_id)
    if not ev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence for regression ID '{regression_id}' not found."
        )
    return ev


@router.get("/deployments", response_model=List[DeploymentItem], tags=["Deployments"])
def get_deployments():
    """Returns recent software deployment events."""
    return integration_client.deployments()


@router.get("/root-cause/{regression_id}", response_model=RCAResponse, tags=["RCA Agent"])
def get_root_cause(regression_id: str):
    """Executes the LangGraph RCA workflow for a regression ID and returns the structured RCA report."""
    return run_rca_workflow(regression_id)


@router.post("/analyze", response_model=RCAResponse, tags=["RCA Agent"])
def post_analyze(request: AnalyzeRequest):
    """Triggers LangGraph RCA workflow with custom request payload."""
    return run_rca_workflow(request.regression_id)
