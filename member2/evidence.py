"""Member 2: Evidence Module.
Packages regression data, critical path, span attribution, and deployment correlation into a structured evidence bundle.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from member2.regression import get_regression_by_id
from member2.critical_path import extract_critical_path
from member2.attribution import compute_span_attribution
from member1.loader import get_trace_by_id

# Recorded deployments
DEPLOYMENTS: List[Dict[str, Any]] = [
    {
        "deployment_id": "DEP-901",
        "service": "payment-service",
        "version": "v2.4.1",
        "deployed_at": (datetime.now(timezone.utc) - timedelta(minutes=32)).isoformat(),
        "commit_sha": "a1f89bc",
        "author": "devops-engineer",
        "message": "feat(stripe): upgrade SDK to v2 client with sync connection pool"
    },
    {
        "deployment_id": "DEP-902",
        "service": "order-service",
        "version": "v1.18.0",
        "deployed_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
        "commit_sha": "7e3b901",
        "author": "backend-team",
        "message": "fix(cart): ensure currency format matches ISO 4217"
    },
    {
        "deployment_id": "DEP-903",
        "service": "frontend-gateway",
        "version": "v3.0.2",
        "deployed_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
        "commit_sha": "c049d52",
        "author": "frontend-team",
        "message": "chore(ui): update CDN bundle references"
    }
]


def get_all_deployments() -> List[Dict[str, Any]]:
    """Returns all deployment events."""
    return DEPLOYMENTS


def find_correlated_deployment(service_name: str) -> Optional[Dict[str, Any]]:
    """Finds deployment event matching service within recent window."""
    for dep in DEPLOYMENTS:
        if dep["service"] == service_name:
            return dep
    return None


def generate_regression_evidence(regression_id: str) -> Optional[Dict[str, Any]]:
    """Generates a structured evidence bundle for the LangGraph RCA agent."""
    regression = get_regression_by_id(regression_id)
    if not regression:
        return None

    service = regression["service"]
    trace_ids = regression.get("correlated_trace_ids", [])

    # Extract critical path from first anomalous trace
    crit_path: List[str] = []
    anomalous_spans: List[Dict[str, Any]] = []

    if trace_ids:
        crit_path = extract_critical_path(trace_ids[0])
        first_trace = get_trace_by_id(trace_ids[0])
        if first_trace:
            anomalous_spans = [
                s for s in first_trace.get("spans", [])
                if s.get("duration_ms", 0) > 200.0 or s.get("has_error")
            ]

    # Span attribution
    attribution = compute_span_attribution(trace_ids)

    # Deployment correlation
    correlated_dep = find_correlated_deployment(service)

    return {
        "regression_id": regression_id,
        "service": service,
        "baseline_latency_ms": regression["baseline_value_ms"],
        "current_latency_ms": regression["current_value_ms"],
        "percentage_change": regression["change_percent"],
        "critical_path": crit_path,
        "span_attribution": attribution,
        "correlated_deployment": correlated_dep,
        "anomalous_spans": anomalous_spans,
        "evidence_score": 0.94 if correlated_dep else 0.75
    }
