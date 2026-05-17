"""
Reusable Plotly chart builders for the HR analytics dashboard.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ENTERPRISE_COLORS = [
    "#1f4e79",
    "#2e75b6",
    "#5b9bd5",
    "#70ad47",
    "#ffc000",
    "#ed7d31",
    "#c55a11",
    "#843c0c",
]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Arial, sans-serif",
        color="#1f2937",
        size=12,
    ),
    margin=dict(l=24, r=24, t=48, b=24),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
)


def _empty_figure(message: str) -> go.Figure:

    figure = go.Figure()
    figure.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#6b7280"),
    )
    figure.update_layout(
        **CHART_LAYOUT,
        height=360,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return figure


def chart_applications_per_job(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No applications per job role for the selected filters."
        )

    frame = pd.DataFrame(rows)
    figure = px.bar(
        frame,
        x="job_title",
        y="application_count",
        color_discrete_sequence=[ENTERPRISE_COLORS[0]],
        labels={
            "job_title": "Job Role",
            "application_count": "Applications",
        },
        title="Applications per Job Role",
    )
    figure.update_layout(**CHART_LAYOUT, height=380)
    figure.update_xaxes(tickangle=-25)
    return figure


def chart_governance_distribution(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No governance flags recorded for the selected filters."
        )

    frame = pd.DataFrame(rows)
    figure = px.pie(
        frame,
        names="governance_flag",
        values="count",
        color_discrete_sequence=ENTERPRISE_COLORS,
        title="Governance Flag Distribution",
        hole=0.45,
    )
    figure.update_layout(**CHART_LAYOUT, height=380)
    return figure


def chart_status_distribution(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No application status data for the selected filters."
        )

    frame = pd.DataFrame(rows)
    figure = px.bar(
        frame,
        x="application_status",
        y="count",
        color="application_status",
        color_discrete_sequence=ENTERPRISE_COLORS,
        labels={
            "application_status": "Status",
            "count": "Applications",
        },
        title="Application Status Distribution",
    )
    figure.update_layout(
        **CHART_LAYOUT,
        height=380,
        showlegend=False,
    )
    return figure


def chart_score_histogram(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No candidate scores available for the selected filters."
        )

    frame = pd.DataFrame(rows)
    figure = px.bar(
        frame,
        x="score_bucket",
        y="count",
        color_discrete_sequence=[ENTERPRISE_COLORS[2]],
        labels={
            "score_bucket": "Score Range",
            "count": "Candidates",
        },
        title="Candidate Score Histogram",
    )
    figure.update_layout(**CHART_LAYOUT, height=380)
    return figure


def chart_shortlisted_vs_pending(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No shortlisted or pending candidates in this period."
        )

    frame = pd.DataFrame(rows)
    figure = px.bar(
        frame,
        x="pipeline_stage",
        y="count",
        color="pipeline_stage",
        color_discrete_sequence=[
            ENTERPRISE_COLORS[3],
            ENTERPRISE_COLORS[4],
            ENTERPRISE_COLORS[5],
        ],
        labels={
            "pipeline_stage": "Pipeline Stage",
            "count": "Applications",
        },
        title="Shortlisted vs Pending Comparison",
    )
    figure.update_layout(
        **CHART_LAYOUT,
        height=380,
        showlegend=False,
    )
    return figure


def chart_audit_activity(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No audit activity recorded for the selected period."
        )

    frame = pd.DataFrame(rows)
    figure = px.bar(
        frame,
        x="action_type",
        y="count",
        color_discrete_sequence=[ENTERPRISE_COLORS[1]],
        labels={
            "action_type": "Audit Action",
            "count": "Events",
        },
        title="Audit Activity Summary",
    )
    figure.update_layout(**CHART_LAYOUT, height=360)
    figure.update_xaxes(tickangle=-20)
    return figure


def chart_recruiter_productivity(rows: list[dict]) -> go.Figure:

    if not rows:

        return _empty_figure(
            "No recruiter feedback actions in the selected period."
        )

    frame = pd.DataFrame(rows)
    figure = px.bar(
        frame,
        x="recruiter_action",
        y="count",
        color_discrete_sequence=[ENTERPRISE_COLORS[6]],
        labels={
            "recruiter_action": "Recruiter Action",
            "count": "Count",
        },
        title="Recruiter Productivity Metrics",
    )
    figure.update_layout(**CHART_LAYOUT, height=360)
    figure.update_xaxes(tickangle=-20)
    return figure
