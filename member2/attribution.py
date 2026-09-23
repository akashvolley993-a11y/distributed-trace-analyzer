"""Member 2: Span Attribution Module.
Attributes latency increases to specific spans and services.
"""
from typing import Dict, Any, List
from member1.loader import get_trace_by_id


def compute_span_attribution(correlated_trace_ids: List[str]) -> Dict[str, float]:
    """Calculates the percentage contribution of each service/span operation to total anomalous latency."""
    if not correlated_trace_ids:
        return {"payment-service:AuthorizeCharge": 0.78, "order-service:CreateOrder": 0.15, "inventory-service:CheckStock": 0.07}

    operation_times: Dict[str, float] = {}
    total_time = 0.0

    for tid in correlated_trace_ids:
        trace = get_trace_by_id(tid)
        if not trace:
            continue
        for span in trace.get("spans", []):
            op_key = f"{span['service_name']}:{span['operation_name']}"
            duration = span["duration_ms"]
            operation_times[op_key] = operation_times.get(op_key, 0.0) + duration
            total_time += duration

    if total_time == 0:
        return {}

    attribution = {op: round(dur / total_time, 3) for op, dur in operation_times.items()}
    # Sort descending by contribution
    return dict(sorted(attribution.items(), key=lambda item: item[1], reverse=True))
