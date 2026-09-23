"""API Client for Streamlit to consume FastAPI endpoints.

Reads API_BASE_URL from environment (.env).
Encapsulates HTTP requests and error handling so the dashboard never accesses
raw data directly.
"""
import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {"error": True, "message": str(e), "endpoint": endpoint}

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.post(url, json=data, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {"error": True, "message": str(e), "endpoint": endpoint}

    def check_health(self) -> Dict[str, Any]:
        return self._get("/health")

    def get_summary(self) -> Dict[str, Any]:
        return self._get("/summary")

    def get_services(self) -> List[str]:
        res = self._get("/services")
        return res if isinstance(res, list) else []

    def get_dependencies(self) -> Dict[str, Any]:
        return self._get("/dependencies")

    def get_traces(self) -> List[Dict[str, Any]]:
        res = self._get("/traces")
        return res if isinstance(res, list) else []

    def get_trace_detail(self, trace_id: str) -> Dict[str, Any]:
        return self._get(f"/trace/{trace_id}")

    def get_latency(self) -> Dict[str, Any]:
        return self._get("/latency")

    def get_regressions(self) -> List[Dict[str, Any]]:
        res = self._get("/regressions")
        return res if isinstance(res, list) else []

    def get_regression_detail(self, regression_id: str) -> Dict[str, Any]:
        return self._get(f"/regression/{regression_id}")

    def get_regression_evidence(self, regression_id: str) -> Dict[str, Any]:
        return self._get(f"/regression/{regression_id}/evidence")

    def get_deployments(self) -> List[Dict[str, Any]]:
        res = self._get("/deployments")
        return res if isinstance(res, list) else []

    def get_root_cause(self, regression_id: str) -> Dict[str, Any]:
        return self._get(f"/root-cause/{regression_id}")

    def trigger_analysis(self, regression_id: str) -> Dict[str, Any]:
        return self._post("/analyze", {"regression_id": regression_id})


api_client = APIClient()
