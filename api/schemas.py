"""Pydantic schemas for API request and response models."""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    service: str = Field(..., example="distributed-trace-backend")
    version: str = Field(..., example="1.0.0")
    timestamp: str


class SummaryResponse(BaseModel):
    services_count: int
    traces_count: int
    active_regressions_count: int
    recent_deployments_count: int
    avg_latency_ms: float
    system_status: str


class ServiceInfo(BaseModel):
    name: str
    status: str
    endpoints: List[str] = []
    average_latency_ms: float


class DependencyEdge(BaseModel):
    source: str
    target: str
    call_count: int = 1
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0


class TopologyResponse(BaseModel):
    services: List[str]
    dependencies: List[DependencyEdge]


class SpanModel(BaseModel):
    span_id: str
    parent_span_id: Optional[str] = None
    trace_id: str
    service_name: str
    operation_name: str
    start_time_offset_ms: float
    duration_ms: float
    status_code: int = 200
    has_error: bool = False
    attributes: Dict[str, Any] = {}


class TraceSummary(BaseModel):
    trace_id: str
    root_service: str
    root_operation: str
    timestamp: str
    duration_ms: float
    span_count: int
    has_error: bool
    status_code: int = 200


class TraceDetail(BaseModel):
    trace_id: str
    root_service: str
    root_operation: str
    timestamp: str
    duration_ms: float
    spans: List[SpanModel]
    critical_path_span_ids: List[str] = []


class LatencyPercentiles(BaseModel):
    p50: float
    p90: float
    p95: float
    p99: float


class LatencyTimeseriesPoint(BaseModel):
    timestamp: str
    service: str
    p50: float
    p95: float
    p99: float


class LatencyResponse(BaseModel):
    overall_percentiles: LatencyPercentiles
    by_service: Dict[str, LatencyPercentiles]
    timeseries: List[LatencyTimeseriesPoint]
    distribution: List[Dict[str, Any]] = []


class RegressionItem(BaseModel):
    regression_id: str
    service: str
    operation: str
    metric: str
    baseline_value_ms: float
    current_value_ms: float
    change_percent: float
    severity: str
    detected_at: str
    status: str
    correlated_trace_ids: List[str] = []


class DeploymentItem(BaseModel):
    deployment_id: str
    service: str
    version: str
    deployed_at: str
    commit_sha: str
    author: str
    message: str


class EvidenceModel(BaseModel):
    regression_id: str
    service: str
    baseline_latency_ms: float
    current_latency_ms: float
    percentage_change: float
    critical_path: List[str]
    span_attribution: Dict[str, float]
    correlated_deployment: Optional[DeploymentItem] = None
    anomalous_spans: List[Dict[str, Any]] = []
    evidence_score: float = 1.0


class RCAResponse(BaseModel):
    regression_id: str
    status: str
    hypothesis: str
    culprit_service: str
    culprit_deployment: Optional[str] = None
    culprit_span: Optional[str] = None
    confidence_score: float
    explanation: str
    evidence_validated: bool
    critical_path_bottleneck: Optional[str] = None
    remediation_recommendations: List[str]
    workflow_steps: List[str] = []


class AnalyzeRequest(BaseModel):
    regression_id: str
