# Distributed Trace Analysis & Root Cause Analysis (RCA) Platform — Member 3

Production-grade integration, backend API, LangGraph RCA AI agent, and Streamlit visualization dashboard for distributed tracing and performance regression analysis.

---

## 🏛️ System Architecture

```text
  Member 1 (Traces & Service Graph)
  ├── data_generator.py
  ├── validation.py
  ├── loader.py
  └── trace_reconstruction.py
            │
            ▼
┌───────────────────────────────────────┐
│     src/integration.py                │
│     (Unified Integration Boundary)    │
└───────────────────────────────────────┘
            ▲
            │
  Member 2 (Analytics & Evidence)
  ├── latency.py
  ├── regression.py
  ├── critical_path.py
  ├── attribution.py
  └── evidence.py
            │
            ▼
┌───────────────────────────────────────┐
│     FastAPI Backend (api/)            │
│     - REST Endpoints                  │
│     - Pydantic Schema Validation      │
│     - Swagger Docs (/docs)            │
└──────────────────┬────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐ ┌─────────────────────────┐
│ Streamlit (app) │ │ LangGraph RCA Agent     │
│ + Plotly Charts │ │ (src/agent.py)          │
└─────────────────┘ └─────────────────────────┘
```

---

## 📂 Project Structure

```text
distributed-trace-analysis/
│
├── api/
│   ├── main.py              # FastAPI application entrypoint & middleware
│   ├── routes.py            # REST API endpoints (health, traces, regressions, RCA)
│   └── schemas.py           # Pydantic request & response models
│
├── app/
│   └── streamlit_app.py     # Interactive dashboard with Plotly charts
│
├── src/
│   ├── agent.py             # LangGraph evidence-based Root Cause Analysis workflow
│   ├── api_client.py        # Streamlit HTTP client wrapper (reads API_BASE_URL)
│   └── integration.py       # Integration adapter for Member 1 & 2 interfaces
│
├── member1/                 # Distributed traces & service dependency modules
│   ├── data_generator.py    # Generates synthetic trace & span trees
│   ├── validation.py        # Validates trace schema and span hierarchy
│   ├── loader.py            # Trace loader and caching
│   └── trace_reconstruction.py # Reconstructs DAGs and service dependencies
│
├── member2/                 # Performance analytics & evidence modules
│   ├── latency.py           # Percentiles (p50, p90, p95, p99) & timeseries
│   ├── regression.py        # Regression detection (baseline vs current)
│   ├── critical_path.py     # Longest execution path along span DAG
│   ├── attribution.py       # Span-level latency attribution
│   └── evidence.py          # Structured evidence bundle builder
│
├── tests/
│   ├── test_api.py          # Core FastAPI endpoint tests
│   ├── test_regression_api.py # Regression, latency & deployment tests
│   └── test_integration.py  # End-to-end integration & RCA agent tests
│
├── .env                     # Local environment configuration
├── .env.example             # Example environment variables template
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Virtual Environment

Ensure Python 3.10+ is installed:

```bash
# Create and activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the FastAPI Backend

```bash
uvicorn api.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### 4. Start the Streamlit Dashboard

In a separate terminal window:

```bash
streamlit run app/streamlit_app.py --server.port 8501
```

- Dashboard URL: `http://localhost:8501`

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check and backend uptime status |
| `GET` | `/summary` | System KPI summary (services, traces, active regressions) |
| `GET` | `/services` | List of all registered microservices |
| `GET` | `/dependencies` | Service dependency graph nodes and call edges |
| `GET` | `/traces` | List of recent trace summaries |
| `GET` | `/trace/{trace_id}` | Detailed trace breakdown with spans and critical path |
| `GET` | `/latency` | Percentiles (p50/p90/p95/p99), timeseries, and distribution |
| `GET` | `/regressions` | All detected performance regressions |
| `GET` | `/regression/{regression_id}` | Specific regression detail |
| `GET` | `/regression/{regression_id}/evidence` | Member 2 evidence bundle for regression |
| `GET` | `/deployments` | History of software deployment events |
| `GET` | `/root-cause/{regression_id}` | Execute LangGraph RCA analysis on regression |
| `POST` | `/analyze` | Trigger RCA analysis with JSON payload `{"regression_id": "..."}` |

---

## 🤖 LangGraph RCA Agent Workflow

The Root Cause Analysis agent strictly follows evidence-grounded reasoning:

```text
START
  ↓
Load Evidence (Member 2 evidence bundle)
  ↓
Validate Evidence (Check completeness, return "Insufficient evidence" if incomplete)
  ↓
Summarize Regression (Quantify baseline vs current latency shift)
  ↓
Explain Critical Path (Highlight bottleneck span sequence)
  ↓
Explain Span Attribution (Calculate operation-level contribution percentage)
  ↓
Explain Deployment Correlation (Correlate with recent code releases)
  ↓
Generate RCA (Synthesize hypothesis, culprit service, culprit deployment, recommendations)
  ↓
Validate RCA (Grounding verification against evidence)
  ↓
END
```

---

## 🤝 How to Connect Member 1 & 2 Code

When your teammates share their files:

1. **Member 1 Files** -> Place in `member1/`:
   - Replace `member1/loader.py` with their data loader.
   - Replace `member1/trace_reconstruction.py` with their reconstruction functions.
2. **Member 2 Files** -> Place in `member2/`:
   - Replace `member2/regression.py` with their regression detection engine.
   - Replace `member2/evidence.py` with their evidence packager.
   - Replace `member2/latency.py` with their latency percentiles calculation.
3. **Verify Connection in `src/integration.py`**:
   - `src/integration.py` delegates to `member1` and `member2`. If their function names differ, adjust the function calls inside `IntegrationClient` in `src/integration.py`.
   - Neither FastAPI nor Streamlit code will need to change!

---

## 🧪 Running Tests

Execute the full automated test suite with pytest:

```bash
pytest tests/ -v
```
