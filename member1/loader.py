"""Member 1: Trace Loader.
Provides data access to trace batches and individual traces.
"""
from typing import List, Dict, Any, Optional
from member1.data_generator import generate_trace_dataset
from member1.validation import validate_trace

_CACHED_TRACES: Optional[List[Dict[str, Any]]] = None


def load_traces(count: int = 20) -> List[Dict[str, Any]]:
    """Loads traces from storage or generator with validation."""
    global _CACHED_TRACES
    if _CACHED_TRACES is None:
        raw_traces = generate_trace_dataset(count=count)
        valid_traces = []
        for t in raw_traces:
            is_valid, _ = validate_trace(t)
            if is_valid:
                valid_traces.append(t)
        _CACHED_TRACES = valid_traces
    return _CACHED_TRACES


def get_trace_by_id(trace_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single trace by ID."""
    traces = load_traces()
    for t in traces:
        if t["trace_id"] == trace_id:
            return t
    return None
