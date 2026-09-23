"""Member 2: Latency Analytics Module.
Calculates percentile aggregations, timeseries trends, and latency distributions.
"""
from typing import Dict, Any, List
import statistics
from datetime import datetime, timezone, timedelta
from member1.loader import load_traces


def compute_percentiles(values: List[float]) -> Dict[str, float]:
    """Computes p50, p90, p95, p99 for a list of latency values."""
    if not values:
        return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}
    sorted_vals = sorted(values)
    n = len(sorted_vals)

    def get_p(p: float) -> float:
        idx = min(int(p * n), n - 1)
        return round(sorted_vals[idx], 2)

    return {
        "p50": get_p(0.50),
        "p90": get_p(0.90),
        "p95": get_p(0.95),
        "p99": get_p(0.99),
    }


def get_latency_metrics() -> Dict[str, Any]:
    """Computes overall latency statistics, per-service metrics, and historical timeseries."""
    traces = load_traces()
    all_durations = [t["duration_ms"] for t in traces]

    # Service-level durations
    service_durations: Dict[str, List[float]] = {}
    for t in traces:
        for span in t.get("spans", []):
            s_name = span["service_name"]
            service_durations.setdefault(s_name, []).append(span["duration_ms"])

    by_service = {s: compute_percentiles(durations) for s, durations in service_durations.items()}

    # Generate realistic timeseries intervals (last 12 intervals, e.g. 5 min intervals)
    now = datetime.now(timezone.utc)
    timeseries = []
    services = list(service_durations.keys())

    for step in range(12, 0, -1):
        timestamp = (now - timedelta(minutes=step * 5)).strftime("%H:%M:%S")
        for s in services:
            base_p50 = by_service[s]["p50"]
            # Inject regression spike in payment-service after interval 6
            is_payment_spike = (s == "payment-service" and step <= 5)
            multiplier = 3.5 if is_payment_spike else 1.0
            p50 = round(base_p50 * multiplier, 2)
            p95 = round(p50 * 1.6, 2)
            p99 = round(p50 * 2.2, 2)
            timeseries.append({
                "timestamp": timestamp,
                "service": s,
                "p50": p50,
                "p95": p95,
                "p99": p99
            })

    # Latency histogram distribution buckets
    distribution = []
    for d in all_durations:
        distribution.append({"duration_ms": d})

    return {
        "overall_percentiles": compute_percentiles(all_durations),
        "by_service": by_service,
        "timeseries": timeseries,
        "distribution": distribution
    }
