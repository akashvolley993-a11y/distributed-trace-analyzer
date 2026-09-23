"""Integration Boundary Layer (Member 3).

This module connects Member 1 (Traces, Topology, Loader) and Member 2
(Regressions, Latency, Critical Path, Attribution, Evidence) to FastAPI,
Streamlit, and the LangGraph RCA Agent.

INTEGRATION INSTRUCTIONS:
When your teammates share their files:
1. Member 1 files go into member1/:
   - data_generator.py -> member1.data_generator
   - validation.py     -> member1.validation
   - loader.py         -> member1.loader
   - trace_reconstruction.py -> member1.trace_reconstruction
2. Member 2 files go into member2/:
   - latency.py        -> member2.latency
   - regression.py     -> member2.regression
   - critical_path.py  -> member2.critical_path
   - attribution.py    -> member2.attribution
   - evidence.py       -> member2.evidence
3. Update the imports or delegate functions in this file if their function names differ.
"""
from typing import List, Dict, Any, Optional

# --- MEMBER 1 MODULE CONNECTIONS ---
try:
    from member1.trace_reconstruction import get_all_services, get_service_dependencies
    from member1.loader import load_traces, get_trace_by_id
except ImportError as e:
    # Graceful fallback if member1 directory is moved or missing
    def get_all_services() -> List[str]:
        return ["frontend-gateway", "order-service", "payment-service", "inventory-service"]

    def get_service_dependencies() -> List[Dict[str, Any]]:
        return [{"source": "frontend-gateway", "target": "order-service", "call_count": 10, "error_rate": 0.0, "avg_latency_ms": 120.0}]

    def load_traces(count: int = 10) -> List[Dict[str, Any]]:
        return []

    def get_trace_by_id(trace_id: str) -> Optional[Dict[str, Any]]:
        return None

# --- MEMBER 2 MODULE CONNECTIONS ---
try:
    from member2.latency import get_latency_metrics
    from member2.regression import get_all_regressions, get_regression_by_id
    from member2.evidence import get_all_deployments, generate_regression_evidence
    from member2.critical_path import extract_critical_path
except ImportError as e:
    # Graceful fallback if member2 directory is moved or missing
    def get_latency_metrics() -> Dict[str, Any]:
        return {"overall_percentiles": {"p50": 50, "p90": 100, "p95": 150, "p99": 200}, "by_service": {}, "timeseries": [], "distribution": []}

    def get_all_regressions() -> List[Dict[str, Any]]:
        return []

    def get_regression_by_id(regression_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_all_deployments() -> List[Dict[str, Any]]:
        return []

    def generate_regression_evidence(regression_id: str) -> Optional[Dict[str, Any]]:
        return None

    def extract_critical_path(trace_id: str) -> List[str]:
        return []


class IntegrationClient:
    """Unified client providing standard data access methods for FastAPI and Streamlit."""

    @staticmethod
    def services() -> List[str]:
        """Fetch all unique microservices (Member 1)."""
        return get_all_services()

    @staticmethod
    def dependencies() -> List[Dict[str, Any]]:
        """Fetch service dependency graph edges (Member 1)."""
        return get_service_dependencies()

    @staticmethod
    def traces() -> List[Dict[str, Any]]:
        """Fetch summary of all recent traces (Member 1)."""
        return load_traces()

    @staticmethod
    def trace(trace_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full trace details and spans (Member 1 & 2 critical path)."""
        data = get_trace_by_id(trace_id)
        if data:
            crit_spans = extract_critical_path(trace_id)
            data["critical_path_span_ids"] = crit_spans
        return data

    @staticmethod
    def latency() -> Dict[str, Any]:
        """Fetch latency statistics and timeseries (Member 2)."""
        return get_latency_metrics()

    @staticmethod
    def regressions() -> List[Dict[str, Any]]:
        """Fetch all detected regressions (Member 2)."""
        return get_all_regressions()

    @staticmethod
    def regression(regression_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific regression by ID (Member 2)."""
        return get_regression_by_id(regression_id)

    @staticmethod
    def deployments() -> List[Dict[str, Any]]:
        """Fetch deployment logs (Member 2)."""
        return get_all_deployments()

    @staticmethod
    def evidence(regression_id: str) -> Optional[Dict[str, Any]]:
        """Fetch structured evidence bundle for a regression (Member 2)."""
        return generate_regression_evidence(regression_id)


# Global singleton instance
integration_client = IntegrationClient()
