"""
Enterprise HR analytics dashboard (Streamlit).
"""

from datetime import date
from datetime import timedelta

import pandas as pd
import requests
import streamlit as st

from analytics_charts import (
    chart_applications_per_job,
    chart_audit_activity,
    chart_governance_distribution,
    chart_recruiter_productivity,
    chart_score_histogram,
    chart_shortlisted_vs_pending,
    chart_status_distribution,
)


def inject_enterprise_styles():
    """Shared CSS for capstone-style enterprise presentation."""

    st.markdown(
        """
        <style>
        .analytics-hero {
            background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%);
            color: #ffffff;
            padding: 1.25rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .analytics-hero h2 {
            color: #ffffff !important;
            margin: 0;
            font-size: 1.6rem;
        }
        .analytics-hero p {
            margin: 0.35rem 0 0 0;
            opacity: 0.92;
        }
        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.65rem 0.85rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        }
        div[data-testid="stMetric"] label {
            color: #475569 !important;
            font-weight: 600;
        }
        .insight-card {
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=60, show_spinner=False)
def fetch_dashboard(
    api_base_url: str,
    start_date: str | None,
    end_date: str | None,
    job_id: int | None,
):

    params = {}

    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    if job_id is not None:
        params["job_id"] = job_id

    response = requests.get(
        f"{api_base_url}/analytics/dashboard",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_export_rows(
    api_base_url: str,
    start_date: str | None,
    end_date: str | None,
    job_id: int | None,
):

    params = {}

    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    if job_id is not None:
        params["job_id"] = job_id

    response = requests.get(
        f"{api_base_url}/analytics/export",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_job_options(api_base_url: str) -> dict[str, int | None]:

    response = requests.get(
        f"{api_base_url}/jobs",
        timeout=15,
    )

    if response.status_code != 200:

        return {"All Jobs": None}

    options = {"All Jobs": None}

    for job in response.json():
        options[f"{job['id']}: {job['title']}"] = job["id"]

    return options


def render_kpi_row(kpis: dict):

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Applications",
        kpis.get("total_applications", 0),
    )
    col2.metric(
        "Shortlisted",
        kpis.get("shortlisted_candidates", 0),
    )
    col3.metric(
        "Pending",
        kpis.get("pending_candidates", 0),
    )
    col4.metric(
        "Rejected",
        kpis.get("rejected_candidates", 0),
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Governance REVIEW",
        kpis.get("governance_review_count", 0),
    )
    col6.metric(
        "Governance ESCALATE",
        kpis.get("governance_escalation_count", 0),
    )
    col7.metric(
        "Avg Candidate Score",
        kpis.get("average_candidate_score", 0),
    )
    col8.metric(
        "SAFE Flags",
        kpis.get("governance_safe_count", 0),
    )


def render_governance_section(
    governance_summary: dict,
    compliance_insights: list[str],
):

    st.markdown("## Governance & Compliance")

    g1, g2, g3 = st.columns(3)

    g1.metric(
        "REVIEW Cases",
        governance_summary.get("review_count", 0),
    )
    g2.metric(
        "ESCALATE Cases",
        governance_summary.get("escalate_count", 0),
    )
    g3.metric(
        "SAFE Cases",
        governance_summary.get("safe_count", 0),
    )

    st.markdown("### Compliance Insights")

    if not compliance_insights:

        st.info(
            "No compliance insights available for the current filters."
        )
        return

    for insight in compliance_insights:
        st.info(insight)


def render_analytics_dashboard(api_base_url: str):

    inject_enterprise_styles()

    st.markdown(
        """
        <div class="analytics-hero">
            <h2>HR Analytics Command Center</h2>
            <p>Enterprise hiring pipeline, governance risk, and recruiter productivity analytics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Filters")

    # Time-based filtering and optional job context.
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(
        [1, 1, 1.2, 0.8]
    )

    default_end = date.today()
    default_start = default_end - timedelta(days=90)

    with filter_col1:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
        )

    with filter_col2:
        end_date = st.date_input(
            "End Date",
            value=default_end,
        )

    job_options = fetch_job_options(api_base_url)

    with filter_col3:
        selected_job_label = st.selectbox(
            "Job Role",
            list(job_options.keys()),
        )
        selected_job_id = job_options[selected_job_label]

    with filter_col4:
        refresh = st.button(
            "Refresh",
            use_container_width=True,
        )

    if refresh:
        st.cache_data.clear()

    start_str = start_date.isoformat()
    end_str = end_date.isoformat()

    if start_date > end_date:

        st.error("Start date must be on or before end date.")
        return

    try:

        with st.spinner("Loading analytics dashboard..."):

            dashboard = fetch_dashboard(
                api_base_url,
                start_str,
                end_str,
                selected_job_id,
            )

    except requests.RequestException as exc:

        st.error(
            "Unable to load analytics data. "
            "Confirm the backend service is running."
        )
        st.caption(str(exc))
        return

    kpis = dashboard.get("kpis", {})

    if (kpis.get("total_applications") or 0) == 0:

        st.warning(
            "No application data matches the selected filters. "
            "Try widening the date range or clearing the job filter."
        )

    st.markdown("## Key Performance Indicators")
    render_kpi_row(kpis)

    st.markdown("---")
    st.markdown("## Pipeline & Role Analytics")

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            chart_applications_per_job(
                dashboard.get("applications_per_job", [])
            ),
            use_container_width=True,
        )

    with chart_right:
        st.plotly_chart(
            chart_status_distribution(
                dashboard.get("status_distribution", [])
            ),
            use_container_width=True,
        )

    chart_left2, chart_right2 = st.columns(2)

    with chart_left2:
        st.plotly_chart(
            chart_governance_distribution(
                dashboard.get("governance_distribution", [])
            ),
            use_container_width=True,
        )

    with chart_right2:
        st.plotly_chart(
            chart_shortlisted_vs_pending(
                dashboard.get("shortlisted_vs_pending", [])
            ),
            use_container_width=True,
        )

    st.plotly_chart(
        chart_score_histogram(
            dashboard.get("score_histogram", [])
        ),
        use_container_width=True,
    )

    render_governance_section(
        dashboard.get("governance_summary", {}),
        dashboard.get("compliance_insights", []),
    )

    st.markdown("---")
    st.markdown("## Operational Intelligence")

    op_left, op_right = st.columns(2)

    with op_left:
        st.plotly_chart(
            chart_audit_activity(
                dashboard.get("audit_activity", [])
            ),
            use_container_width=True,
        )

    with op_right:
        st.plotly_chart(
            chart_recruiter_productivity(
                dashboard.get("recruiter_productivity", [])
            ),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("## Export")

    try:

        export_rows = fetch_export_rows(
            api_base_url,
            start_str,
            end_str,
            selected_job_id,
        )

    except requests.RequestException:

        export_rows = []

    if not export_rows:

        st.info(
            "No rows available for CSV export with the current filters."
        )
        return

    export_df = pd.DataFrame(export_rows)

    st.dataframe(
        export_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download CSV Analytics Report",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=(
            f"hireguard_analytics_{start_str}_{end_str}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )
