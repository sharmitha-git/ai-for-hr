from datetime import date
from datetime import datetime
from typing import Any

from repositories.analytics_repository import (
    AnalyticsRepository
)


class AnalyticsService:
    """
    Service layer for HR analytics dashboard payloads.
    Aggregates repository data and adds derived compliance insights.
    """

    @staticmethod
    def _parse_date(
        value: str | date | datetime | None,
    ) -> date | datetime | None:

        if value is None or value == "":

            return None

        if isinstance(value, datetime):

            return value

        if isinstance(value, date):

            return value

        return datetime.strptime(
            str(value),
            "%Y-%m-%d",
        ).date()

    @staticmethod
    def get_dashboard(
        start_date=None,
        end_date=None,
        job_id: int | None = None,
    ) -> dict[str, Any]:

        start = AnalyticsService._parse_date(start_date)
        end = AnalyticsService._parse_date(end_date)

        kpis = AnalyticsRepository.get_kpi_summary(
            start,
            end,
            job_id,
        )

        governance_distribution = (
            AnalyticsRepository.get_governance_distribution(
                start,
                end,
                job_id,
            )
        )

        governance_insights = (
            AnalyticsService._build_compliance_insights(
                kpis,
                governance_distribution,
            )
        )

        return {
            "filters": {
                "start_date": (
                    start.isoformat()
                    if isinstance(start, (date, datetime))
                    else None
                ),
                "end_date": (
                    end_date
                    if isinstance(end_date, str)
                    else (
                        end.isoformat()
                        if isinstance(end, (date, datetime))
                        else None
                    )
                ),
                "job_id": job_id,
            },
            "kpis": kpis,
            "applications_per_job": (
                AnalyticsRepository.get_applications_per_job(
                    start,
                    end,
                    job_id,
                )
            ),
            "governance_distribution": (
                governance_distribution
            ),
            "status_distribution": (
                AnalyticsRepository.get_status_distribution(
                    start,
                    end,
                    job_id,
                )
            ),
            "score_histogram": (
                AnalyticsRepository.get_score_histogram(
                    start,
                    end,
                    job_id,
                )
            ),
            "shortlisted_vs_pending": (
                AnalyticsRepository.get_shortlisted_vs_pending(
                    start,
                    end,
                    job_id,
                )
            ),
            "governance_summary": {
                "review_count": kpis.get(
                    "governance_review_count",
                    0,
                ),
                "escalate_count": kpis.get(
                    "governance_escalation_count",
                    0,
                ),
                "safe_count": kpis.get(
                    "governance_safe_count",
                    0,
                ),
                "distribution": governance_distribution,
            },
            "compliance_insights": governance_insights,
            "audit_activity": (
                AnalyticsRepository.get_audit_activity_summary(
                    start,
                    end,
                )
            ),
            "recruiter_productivity": (
                AnalyticsRepository.get_recruiter_productivity(
                    start,
                    end,
                )
            ),
        }

    @staticmethod
    def get_export_dataset(
        start_date=None,
        end_date=None,
        job_id: int | None = None,
    ) -> list[dict[str, Any]]:

        start = AnalyticsService._parse_date(start_date)
        end = AnalyticsService._parse_date(end_date)

        return AnalyticsRepository.get_export_rows(
            start,
            end,
            job_id,
        )

    @staticmethod
    def _build_compliance_insights(
        kpis: dict[str, Any],
        governance_distribution: list[dict[str, Any]],
    ) -> list[str]:

        total = kpis.get("total_applications", 0) or 0
        review = kpis.get("governance_review_count", 0) or 0
        escalate = kpis.get(
            "governance_escalation_count",
            0,
        ) or 0

        insights: list[str] = []

        if total == 0:

            insights.append(
                "No applications in the selected period. "
                "Upload candidates or widen the date filter."
            )
            return insights

        review_pct = round(
            (review / total) * 100,
            1,
        )
        escalate_pct = round(
            (escalate / total) * 100,
            1,
        )

        insights.append(
            f"{review_pct}% of applications require governance REVIEW."
        )
        insights.append(
            f"{escalate_pct}% of applications are flagged for ESCALATE."
        )

        if escalate > 0:

            insights.append(
                "Escalated cases should be reviewed before "
                "final hiring decisions per compliance policy."
            )

        if review + escalate == 0:

            insights.append(
                "All applications are currently in SAFE governance "
                "status for the selected filters."
            )

        top_flag = (
            governance_distribution[0]["governance_flag"]
            if governance_distribution
            else "N/A"
        )
        insights.append(
            f"Dominant governance flag: {top_flag}."
        )

        return insights
