"""Member 2: Regression Detection Module.
Identifies performance regressions by comparing baseline and current telemetry windows.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

# Realistic detected regressions based on simulated telemetry
REGRESSION_DATA: List[Dict[str, Any]] = [
    {
        "regression_id": "REG-101",
        "service": "payment-service",
        "operation": "AuthorizeCharge",
        "metric": "p95_latency",
        "baseline_value_ms": 72.5,
        "current_value_ms": 485.0,
        "change_percent": 569.0,
        "severity": "CRITICAL",
        "detected_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
        "status": "ACTIVE",
        "correlated_trace_ids": ["trace-1000", "trace-1004", "trace-1008", "trace-1012"]
    },
    {
        "regression_id": "REG-102",
        "service": "order-service",
        "operation": "CreateOrder",
        "metric": "p95_latency",
        "baseline_value_ms": 285.0,
        "current_value_ms": 760.0,
        "change_percent": 166.7,
        "severity": "HIGH",
        "detected_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
        "status": "ACTIVE",
        "correlated_trace_ids": ["trace-1000", "trace-1004"]
    },
    {
        "regression_id": "REG-103",
        "service": "inventory-service",
        "operation": "CheckStock",
        "metric": "error_rate",
        "baseline_value_ms": 0.01,
        "current_value_ms": 0.04,
        "change_percent": 300.0,
        "severity": "MEDIUM",
        "detected_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        "status": "RESOLVED",
        "correlated_trace_ids": []
    }
]


def get_all_regressions() -> List[Dict[str, Any]]:
    """Returns all detected performance regressions."""
    return REGRESSION_DATA


def get_regression_by_id(regression_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves single regression information by ID."""
    for reg in REGRESSION_DATA:
        if reg["regression_id"] == regression_id:
            return reg
    return None
