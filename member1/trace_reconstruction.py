"""Member 1: Trace Reconstruction.
Reconstructs span DAGs, discovers microservices, and computes service dependency graphs.
"""
from typing import List, Dict, Any, Set
from member1.loader import load_traces


def get_all_services() -> List[str]:
    """Extracts all unique active service names from traces."""
    traces = load_traces()
    services: Set[str] = set()
    for trace in traces:
        for span in trace.get("spans", []):
            services.add(span["service_name"])
    return sorted(list(services))


def get_service_dependencies() -> List[Dict[str, Any]]:
    """Builds service-to-service call dependency edges from parent-child span pairs."""
    traces = load_traces()
    edge_stats: Dict[tuple, Dict[str, Any]] = {}

    for trace in traces:
        spans = trace.get("spans", [])
        span_by_id = {s["span_id"]: s for s in spans}

        for span in spans:
            parent_id = span.get("parent_span_id")
            if parent_id and parent_id in span_by_id:
                parent_span = span_by_id[parent_id]
                source = parent_span["service_name"]
                target = span["service_name"]

                if source != target:  # cross-service invocation
                    key = (source, target)
                    if key not in edge_stats:
                        edge_stats[key] = {
                            "source": source,
                            "target": target,
                            "call_count": 0,
                            "total_duration": 0.0,
                            "error_count": 0,
                        }
                    edge_stats[key]["call_count"] += 1
                    edge_stats[key]["total_duration"] += span["duration_ms"]
                    if span.get("has_error"):
                        edge_stats[key]["error_count"] += 1

    dependencies = []
    for (src, tgt), stats in edge_stats.items():
        calls = stats["call_count"]
        dependencies.append({
            "source": src,
            "target": tgt,
            "call_count": calls,
            "error_rate": round(stats["error_count"] / max(1, calls), 3),
            "avg_latency_ms": round(stats["total_duration"] / max(1, calls), 2)
        })

    return sorted(dependencies, key=lambda x: (x["source"], x["target"]))
