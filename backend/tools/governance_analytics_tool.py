from backend.tools.tool_registry import (
    register_tool
)

from repositories.analytics_repository import (
    AnalyticsRepository
)


@register_tool(
    "governance_statistics"
)
def governance_statistics():

    # Reuse dashboard aggregation queries to avoid duplicated SQL logic.
    kpis = AnalyticsRepository.get_kpi_summary()

    return {
        "total_applications":
            kpis.get("total_applications", 0),
        "review_count":
            kpis.get("governance_review_count", 0),
        "safe_count":
            kpis.get("governance_safe_count", 0),
        "escalate_count":
            kpis.get("governance_escalation_count", 0),
        "shortlisted_count":
            kpis.get("shortlisted_candidates", 0),
        "rejected_count":
            kpis.get("rejected_candidates", 0),
        "under_review_count":
            kpis.get("pending_candidates", 0),
        "average_score":
            kpis.get("average_candidate_score", 0),
    }
