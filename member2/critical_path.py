"""Member 2: Critical Path Analysis Module.
Calculates the sequence of dependent spans along the critical execution path of a trace.
"""
from typing import List, Dict, Any, Optional
from member1.loader import get_trace_by_id


def extract_critical_path(trace_id: str) -> List[str]:
    """Finds the span IDs along the longest dependent execution path for a trace."""
    trace = get_trace_by_id(trace_id)
    if not trace:
        return []

    spans = trace.get("spans", [])
    if not spans:
        return []

    # Map span parent relationships
    children_map: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for s in spans:
        parent = s.get("parent_span_id")
        children_map.setdefault(parent, []).append(s)

    # Traverse from root along largest duration child branch
    critical_span_ids = []
    current_parent: Optional[str] = None

    while True:
        children = children_map.get(current_parent, [])
        if not children:
            break
        # Pick the child span with largest duration
        longest_child = max(children, key=lambda x: x["duration_ms"])
        critical_span_ids.append(longest_child["span_id"])
        current_parent = longest_child["span_id"]

    return critical_span_ids
