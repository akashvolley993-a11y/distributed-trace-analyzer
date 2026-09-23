"""Streamlit Dashboard for Distributed Trace Analysis & RCA (Member 3).

Visualizes telemetry and RCA results returned strictly by FastAPI.
All charts rendered via Plotly without local calculations.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math
import sys
import os

# Ensure root directory is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api_client import api_client, API_BASE_URL

st.set_page_config(
    page_title="Distributed Trace & RCA Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E222D;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 12px;
    }
    .status-badge-active {
        color: #EF4444;
        font-weight: bold;
        background-color: rgba(239, 68, 68, 0.15);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .status-badge-resolved {
        color: #10B981;
        font-weight: bold;
        background-color: rgba(16, 185, 129, 0.15);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .rca-card {
        background-color: #1a2332;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #2563eb;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔍 Trace & RCA Hub")
st.sidebar.caption("Member 3: Integration, API & Agent")

st.sidebar.markdown(f"**Target API:** `{API_BASE_URL}`")
health_check = api_client.check_health()
is_online = health_check.get("status") == "ok" if isinstance(health_check, dict) else False

if is_online:
    st.sidebar.success("● FastAPI Connected")
else:
    st.sidebar.error("● FastAPI Offline")
    st.sidebar.info("Run `uvicorn api.main:app --reload` to start the backend.")

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("""
### Architecture Flow
1. **Member 1**: Traces & Dependency DAG
2. **Member 2**: Regressions & Evidence
3. **FastAPI**: Validated REST Endpoints
4. **LangGraph**: Structured RCA Agent
5. **Streamlit**: Plotly Visualization
""")

# Top Overview KPI banner
summary = api_client.get_summary()
if isinstance(summary, dict) and not summary.get("error"):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Microservices", summary.get("services_count", 0))
    col2.metric("Recorded Traces", summary.get("traces_count", 0))
    col3.metric("Active Regressions", summary.get("active_regressions_count", 0), delta="Critical" if summary.get("active_regressions_count", 0) > 0 else None, delta_color="inverse")
    col4.metric("Recent Deployments", summary.get("recent_deployments_count", 0))
    col5.metric("System P50 Latency", f"{summary.get('avg_latency_ms', 0):.1f} ms")
else:
    st.warning("⚠️ Waiting for FastAPI backend to respond. Showing sample views.")

# Tabs Navigation
tab_topo, tab_latency, tab_regressions, tab_traces, tab_rca = st.tabs([
    "🕸️ Service Topology",
    "📈 Latency & Trends",
    "🚨 Regressions & Deployments",
    "📊 Traces & Critical Path",
    "🤖 LangGraph RCA Agent"
])

# ==============================================================================
# TAB 1: SERVICE TOPOLOGY (DEPENDENCIES GRAPH)
# ==============================================================================
with tab_topo:
    st.subheader("Service Dependency Graph (Member 1 via API)")
    st.caption("Visualizing service-to-service communication edges and cross-service invocation latency.")

    topo_data = api_client.get_dependencies()
    if isinstance(topo_data, dict) and "services" in topo_data:
        services = topo_data.get("services", [])
        dependencies = topo_data.get("dependencies", [])

        # Build network graph using Plotly
        n_services = len(services)
        positions = {}
        for i, s in enumerate(services):
            angle = (2 * math.pi * i) / max(1, n_services)
            positions[s] = (math.cos(angle) * 10, math.sin(angle) * 10)

        edge_x, edge_y = [], []
        edge_texts = []
        for dep in dependencies:
            src = dep["source"]
            tgt = dep["target"]
            if src in positions and tgt in positions:
                x0, y0 = positions[src]
                x1, y1 = positions[tgt]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color="#64748B"),
            hoverinfo="none",
            mode="lines"
        )

        node_x = [positions[s][0] for s in services]
        node_y = [positions[s][1] for s in services]
        node_text = [f"<b>{s}</b>" for s in services]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=node_text,
            textposition="top center",
            marker=dict(
                color=["#EF4444" if "payment" in s else "#3B82F6" for s in services],
                size=28,
                line=dict(width=2, color="#FFFFFF")
            )
        )

        fig_topo = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=20, r=20, t=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
        )
        st.plotly_chart(fig_topo, use_container_width=True)

        # Show dependency table
        if dependencies:
            st.markdown("#### Dependency Call Metrics")
            df_dep = pd.DataFrame(dependencies)
            st.dataframe(df_dep, use_container_width=True)
    else:
        st.info("No dependency data returned from API.")

# ==============================================================================
# TAB 2: LATENCY & TRENDS (PLOTLY LINE & HISTOGRAM)
# ==============================================================================
with tab_latency:
    st.subheader("Latency Analytics & Trends (Member 2 via API)")
    st.caption("P95/P99 line trends and latency distribution histogram strictly populated from API.")

    lat_data = api_client.get_latency()
    if isinstance(lat_data, dict) and "timeseries" in lat_data:
        ts_data = lat_data.get("timeseries", [])
        if ts_data:
            df_ts = pd.DataFrame(ts_data)
            
            # Line chart: P95 and P99 over time
            col_l1, col_l2 = st.columns([2, 1])
            with col_l1:
                st.markdown("#### P95 Latency by Service")
                fig_line = px.line(
                    df_ts,
                    x="timestamp",
                    y="p95",
                    color="service",
                    markers=True,
                    labels={"p95": "P95 Latency (ms)", "timestamp": "Time"},
                    title="P95 Latency Timeline Across Services"
                )
                fig_line.update_layout(height=380, template="plotly_dark")
                st.plotly_chart(fig_line, use_container_width=True)

            with col_l2:
                st.markdown("#### Service Percentiles (Current)")
                by_svc = lat_data.get("by_service", {})
                if by_svc:
                    svc_rows = []
                    for s, p in by_svc.items():
                        svc_rows.append({"Service": s, "P50 (ms)": p["p50"], "P95 (ms)": p["p95"], "P99 (ms)": p["p99"]})
                    st.dataframe(pd.DataFrame(svc_rows), use_container_width=True)

        # Histogram of latency distribution
        dist_data = lat_data.get("distribution", [])
        if dist_data:
            st.markdown("#### Latency Distribution Histogram")
            df_dist = pd.DataFrame(dist_data)
            fig_hist = px.histogram(
                df_dist,
                x="duration_ms",
                nbins=15,
                labels={"duration_ms": "Trace Duration (ms)"},
                title="Overall Trace Duration Distribution"
            )
            fig_hist.update_layout(height=320, template="plotly_dark")
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Latency metrics unavailable from backend API.")

# ==============================================================================
# TAB 3: REGRESSIONS & DEPLOYMENTS (TIMELINE & COMPARISON)
# ==============================================================================
with tab_regressions:
    st.subheader("Performance Regressions & Correlated Releases")
    st.caption("Visualizing detected regressions alongside recent deployment events.")

    regressions = api_client.get_regressions()
    deployments = api_client.get_deployments()

    col_r1, col_r2 = st.columns([3, 2])

    with col_r1:
        st.markdown("#### Detected Performance Regressions")
        if regressions and isinstance(regressions, list):
            for reg in regressions:
                sev_color = "red" if reg.get("severity") == "CRITICAL" else "orange"
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#F3F4F6;">{reg.get('regression_id')} — {reg.get('service')} ({reg.get('operation')})</h4>
                        <span style="color:{sev_color}; font-weight:bold; border: 1px solid {sev_color}; padding: 2px 6px; border-radius:4px;">
                            {reg.get('severity')} ({reg.get('status')})
                        </span>
                    </div>
                    <p style="margin: 8px 0 4px 0; color:#9CA3AF;">Metric: <code>{reg.get('metric')}</code> | Detected: {reg.get('detected_at')}</p>
                    <div style="display:flex; gap:20px; font-size:14px; margin-top:6px;">
                        <span>Baseline: <b>{reg.get('baseline_value_ms')} ms</b></span>
                        <span>Current: <b>{reg.get('current_value_ms')} ms</b></span>
                        <span style="color:#EF4444;">Shift: <b>+{reg.get('change_percent')}%</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Before / After Comparison Chart
            st.markdown("#### Before vs After Latency Comparison")
            df_reg = pd.DataFrame(regressions)
            if not df_reg.empty and "baseline_value_ms" in df_reg:
                fig_comp = go.Figure(data=[
                    go.Bar(name='Baseline (ms)', x=df_reg['regression_id'], y=df_reg['baseline_value_ms'], marker_color='#3B82F6'),
                    go.Bar(name='Current (ms)', x=df_reg['regression_id'], y=df_reg['current_value_ms'], marker_color='#EF4444')
                ])
                fig_comp.update_layout(barmode='group', height=300, template="plotly_dark")
                st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No active regressions detected.")

    with col_r2:
        st.markdown("#### Deployment Events Timeline")
        if deployments and isinstance(deployments, list):
            df_dep = pd.DataFrame(deployments)
            for dep in deployments:
                st.markdown(f"""
                <div style="background-color:#1E222D; padding:12px; border-radius:6px; margin-bottom:8px; border-left:3px solid #10B981;">
                    <b>{dep.get('deployment_id')}</b>: <code>{dep.get('service')}</code> @ <b>{dep.get('version')}</b>
                    <br><small style="color:#9CA3AF;">Author: {dep.get('author')} | {dep.get('deployed_at')}</small>
                    <br><span style="font-size:13px;">💬 {dep.get('message')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No deployment history found.")

# ==============================================================================
# TAB 4: TRACES & CRITICAL PATH WATERFALL (PLOTLY GANTT)
# ==============================================================================
with tab_traces:
    st.subheader("Distributed Traces & Critical Path Waterfall (Plotly)")
    st.caption("Interactive waterfall timeline mapping span latency and critical path.")

    traces = api_client.get_traces()
    if traces and isinstance(traces, list):
        trace_ids = [t["trace_id"] for t in traces]
        selected_tid = st.selectbox("Select Trace to Inspect:", trace_ids)

        if selected_tid:
            trace_detail = api_client.get_trace_detail(selected_tid)
            if trace_detail and "spans" in trace_detail:
                spans = trace_detail.get("spans", [])
                crit_ids = set(trace_detail.get("critical_path_span_ids", []))

                st.markdown(f"**Trace:** `{trace_detail['trace_id']}` | **Root:** `{trace_detail['root_service']}` | **Duration:** `{trace_detail['duration_ms']} ms`")

                # Build Waterfall Gantt chart using Plotly
                span_rows = []
                for s in spans:
                    is_crit = s["span_id"] in crit_ids
                    span_rows.append({
                        "Task": f"{s['service_name']}: {s['operation_name']}",
                        "Start": s["start_time_offset_ms"],
                        "Duration": s["duration_ms"],
                        "Service": s["service_name"],
                        "CriticalPath": "Yes (Bottleneck)" if is_crit else "No",
                        "Error": "ERROR" if s.get("has_error") else "OK"
                    })

                df_spans = pd.DataFrame(span_rows)

                # Horizontal bar chart representing span execution offsets and durations
                fig_waterfall = go.Figure()
                for _, row in df_spans.iterrows():
                    color = "#EF4444" if row["CriticalPath"] == "Yes (Bottleneck)" else ("#F59E0B" if row["Error"] == "ERROR" else "#3B82F6")
                    fig_waterfall.add_trace(go.Bar(
                        y=[row["Task"]],
                        x=[row["Duration"]],
                        base=[row["Start"]],
                        orientation='h',
                        name=row["Service"],
                        marker=dict(color=color),
                        text=f"{row['Duration']:.1f} ms",
                        textposition='auto',
                        hoverinfo="text",
                        hovertext=f"Service: {row['Service']}<br>Duration: {row['Duration']} ms<br>Offset: {row['Start']} ms<br>Critical Path: {row['CriticalPath']}"
                    ))

                fig_waterfall.update_layout(
                    title=f"Span Execution Waterfall for {selected_tid}",
                    xaxis_title="Time Offset from Root Request (ms)",
                    yaxis=dict(autorange="reversed"),
                    showlegend=False,
                    height=350,
                    template="plotly_dark"
                )
                st.plotly_chart(fig_waterfall, use_container_width=True)

                st.markdown("#### Raw Span Telemetry")
                st.dataframe(pd.DataFrame(spans)[["span_id", "service_name", "operation_name", "duration_ms", "has_error", "status_code"]], use_container_width=True)
    else:
        st.info("No trace data returned by API.")

# ==============================================================================
# TAB 5: LANGGRAPH ROOT CAUSE ANALYSIS (RCA) AGENT
# ==============================================================================
with tab_rca:
    st.subheader("🤖 LangGraph Root Cause Analysis (RCA) Agent")
    st.caption("AI-driven agent synthesizing Member 2 evidence to identify regression culprits without guesswork.")

    regressions = api_client.get_regressions()
    if regressions and isinstance(regressions, list):
        reg_ids = [r["regression_id"] for r in regressions]
        selected_reg_id = st.selectbox("Select Target Regression:", reg_ids, key="rca_select")

        col_act1, col_act2 = st.columns([1, 4])
        with col_act1:
            run_btn = st.button("🚀 Run LangGraph RCA", type="primary")

        if run_btn:
            with st.spinner(f"Executing LangGraph workflow for {selected_reg_id}..."):
                rca_result = api_client.trigger_analysis(selected_reg_id)

            if rca_result and not rca_result.get("error"):
                # Workflow steps execution progression
                st.markdown("#### Workflow Step-by-Step Trajectory")
                steps = rca_result.get("workflow_steps", [])
                for idx, step in enumerate(steps, 1):
                    icon = "✅" if "PASSED" in step or "Completed" in step or "Formulated" in step else "🔹"
                    st.write(f"{icon} **Step {idx}:** {step}")

                # RCA Findings Card
                confidence = rca_result.get("confidence_score", 0.0)
                conf_color = "#10B981" if confidence >= 80 else ("#F59E0B" if confidence >= 50 else "#EF4444")

                st.markdown(f"""
                <div class="rca-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#60A5FA;">Root Cause Analysis Report</h3>
                        <span style="font-size:16px; font-weight:bold; color:{conf_color};">
                            Confidence: {confidence:.0f}%
                        </span>
                    </div>
                    <hr style="border-color:#3B82F6; margin:12px 0;">
                    <p style="font-size:16px; color:#F3F4F6;"><b>Hypothesis:</b> {rca_result.get('hypothesis')}</p>
                    <div style="display:flex; gap:30px; margin: 12px 0; font-size:14px; color:#9CA3AF;">
                        <div>Culprit Service: <code style="color:#60A5FA;">{rca_result.get('culprit_service')}</code></div>
                        <div>Culprit Deployment: <code style="color:#34D399;">{rca_result.get('culprit_deployment', 'N/A')}</code></div>
                        <div>Culprit Span: <code style="color:#F87171;">{rca_result.get('culprit_span', 'N/A')}</code></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.markdown("#### Detailed Diagnostic Evidence")
                    st.text(rca_result.get("explanation", ""))

                with col_e2:
                    st.markdown("#### Recommended Remediation Actions")
                    recs = rca_result.get("remediation_recommendations", [])
                    for r in recs:
                        st.info(f"💡 {r}")
            else:
                st.error(f"Error running RCA analysis: {rca_result.get('message', 'Unknown error')}")
    else:
        st.info("No regressions available to analyze.")
