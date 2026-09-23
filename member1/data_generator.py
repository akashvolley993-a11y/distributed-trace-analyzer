"""Member 1: Data Generator.
Generates synthetic distributed trace spans and telemetry data for microservices.
Teammates can replace this file with their actual implementation.
"""
from typing import List, Dict, Any
import time
import random
from datetime import datetime, timezone, timedelta

SERVICES = [
    "frontend-gateway",
    "order-service",
    "payment-service",
    "inventory-service",
    "notification-service",
    "database-cluster",
]

OPERATIONS = {
    "frontend-gateway": ["GET /checkout", "POST /orders", "GET /products", "GET /profile"],
    "order-service": ["CreateOrder", "ValidateCart", "FetchOrderHistory", "CancelOrder"],
    "payment-service": ["AuthorizeCharge", "ProcessCard", "RefundTransaction"],
    "inventory-service": ["CheckStock", "ReserveItems", "ReleaseStock"],
    "notification-service": ["SendEmailConfirmation", "SendPushNotification"],
    "database-cluster": ["SELECT * FROM orders", "UPDATE inventory SET qty = qty - 1", "INSERT INTO payments"],
}


def generate_trace_dataset(count: int = 15) -> List[Dict[str, Any]]:
    """Generates a list of structured traces with realistic span trees."""
    traces = []
    base_time = datetime.now(timezone.utc) - timedelta(minutes=45)

    for i in range(count):
        trace_id = f"trace-{1000 + i}"
        has_anomaly = (i % 4 == 0)  # some traces contain slow/regressed spans
        start_time = base_time + timedelta(minutes=i * 3)
        iso_start = start_time.isoformat()

        root_op = "POST /orders" if i % 2 == 0 else "GET /checkout"

        spans = []
        # Span 1: Root - frontend-gateway
        frontend_duration = 320.0 + (550.0 if has_anomaly else 0.0)
        spans.append({
            "span_id": f"{trace_id}-s1",
            "parent_span_id": None,
            "trace_id": trace_id,
            "service_name": "frontend-gateway",
            "operation_name": root_op,
            "start_time_offset_ms": 0.0,
            "duration_ms": frontend_duration,
            "status_code": 200,
            "has_error": False,
            "attributes": {"http.method": "POST", "http.url": f"/api/v1{root_op.split()[-1]}"}
        })

        # Span 2: order-service child
        order_duration = 270.0 + (480.0 if has_anomaly else 0.0)
        spans.append({
            "span_id": f"{trace_id}-s2",
            "parent_span_id": f"{trace_id}-s1",
            "trace_id": trace_id,
            "service_name": "order-service",
            "operation_name": "CreateOrder",
            "start_time_offset_ms": 25.0,
            "duration_ms": order_duration,
            "status_code": 200,
            "has_error": False,
            "attributes": {"order.items_count": 3}
        })

        # Span 3: inventory-service check
        inv_duration = 45.0 + random.uniform(5.0, 15.0)
        spans.append({
            "span_id": f"{trace_id}-s3",
            "parent_span_id": f"{trace_id}-s2",
            "trace_id": trace_id,
            "service_name": "inventory-service",
            "operation_name": "CheckStock",
            "start_time_offset_ms": 35.0,
            "duration_ms": inv_duration,
            "status_code": 200,
            "has_error": False,
            "attributes": {"stock.available": True}
        })

        # Span 4: payment-service authorize (this is the culprit in anomalies!)
        pay_duration = (420.0 + random.uniform(20.0, 80.0)) if has_anomaly else (65.0 + random.uniform(5.0, 20.0))
        pay_error = has_anomaly and (i % 8 == 0)
        spans.append({
            "span_id": f"{trace_id}-s4",
            "parent_span_id": f"{trace_id}-s2",
            "trace_id": trace_id,
            "service_name": "payment-service",
            "operation_name": "AuthorizeCharge",
            "start_time_offset_ms": 90.0,
            "duration_ms": pay_duration,
            "status_code": 500 if pay_error else 200,
            "has_error": pay_error,
            "attributes": {
                "payment.gateway": "StripeV2",
                "payment.amount_usd": 89.99,
                "error.message": "GatewayTimeout: Downstream connection pool exhausted" if pay_error else None
            }
        })

        # Span 5: database query
        db_duration = 30.0 + random.uniform(5.0, 15.0)
        spans.append({
            "span_id": f"{trace_id}-s5",
            "parent_span_id": f"{trace_id}-s4",
            "trace_id": trace_id,
            "service_name": "database-cluster",
            "operation_name": "INSERT INTO payments",
            "start_time_offset_ms": 110.0,
            "duration_ms": db_duration,
            "status_code": 200,
            "has_error": False,
            "attributes": {"db.system": "postgresql", "db.statement": "INSERT INTO payments ..."}
        })

        total_duration = max(s["start_time_offset_ms"] + s["duration_ms"] for s in spans)

        traces.append({
            "trace_id": trace_id,
            "root_service": "frontend-gateway",
            "root_operation": root_op,
            "timestamp": iso_start,
            "duration_ms": round(total_duration, 2),
            "span_count": len(spans),
            "has_error": any(s["has_error"] for s in spans),
            "status_code": 500 if any(s["has_error"] for s in spans) else 200,
            "spans": spans,
        })

    return traces
