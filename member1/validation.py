"""Member 1: Trace validation module.
Validates trace structures, timestamps, and span relationships.
"""
from typing import Dict, Any, List, Tuple


def validate_span(span: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates an individual span structure."""
    errors = []
    required_fields = ["span_id", "trace_id", "service_name", "operation_name", "duration_ms"]
    for field in required_fields:
        if field not in span:
            errors.append(f"Missing required span field: '{field}'")
    if "duration_ms" in span and span["duration_ms"] < 0:
        errors.append("Duration cannot be negative")
    return len(errors) == 0, errors


def validate_trace(trace: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates an entire trace including parent-child span integrity."""
    errors = []
    if "trace_id" not in trace:
        errors.append("Trace missing trace_id")
        return False, errors

    spans = trace.get("spans", [])
    if not spans:
        errors.append(f"Trace {trace['trace_id']} has no spans")
        return False, errors

    span_ids = {s.get("span_id") for s in spans}
    has_root = False

    for span in spans:
        valid, span_errs = validate_span(span)
        errors.extend(span_errs)
        parent_id = span.get("parent_span_id")
        if parent_id is None:
            has_root = True
        elif parent_id not in span_ids:
            errors.append(f"Span {span.get('span_id')} references missing parent {parent_id}")

    if not has_root:
        errors.append("Trace lacks a root span (parent_span_id is None)")

    return len(errors) == 0, errors
