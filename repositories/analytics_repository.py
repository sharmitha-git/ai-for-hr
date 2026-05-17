from datetime import date
from datetime import datetime
from typing import Any

from sqlalchemy import text

from database.connection import engine


class AnalyticsRepository:
    """
    PostgreSQL aggregation queries for the HR analytics dashboard.
    All methods accept optional date and job filters to avoid duplicated SQL.
    """

    @staticmethod
    def _filter_clause(
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
        job_id: int | None = None,
        table_alias: str = "a",
    ) -> tuple[str, dict[str, Any]]:

        clauses = ["1=1"]
        params: dict[str, Any] = {}

        if start_date is not None:
            clauses.append(
                f"DATE({table_alias}.created_at) >= :start_date"
            )
            if isinstance(start_date, datetime):
                params["start_date"] = start_date.date()
            else:
                params["start_date"] = start_date

        if end_date is not None:
            clauses.append(
                f"DATE({table_alias}.created_at) <= :end_date"
            )
            if isinstance(end_date, datetime):
                params["end_date"] = end_date.date()
            else:
                params["end_date"] = end_date

        if job_id is not None:
            clauses.append(
                f"{table_alias}.job_id = :job_id"
            )
            params["job_id"] = job_id

        return " AND ".join(clauses), params

    @staticmethod
    def get_kpi_summary(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> dict[str, Any]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                COUNT(*)::int AS total_applications,
                COUNT(*) FILTER (
                    WHERE application_status = 'SHORTLISTED'
                )::int AS shortlisted_candidates,
                COUNT(*) FILTER (
                    WHERE COALESCE(application_status, 'PENDING')
                    IN ('PENDING', 'UNDER_REVIEW')
                )::int AS pending_candidates,
                COUNT(*) FILTER (
                    WHERE application_status = 'REJECTED'
                )::int AS rejected_candidates,
                COUNT(*) FILTER (
                    WHERE governance_flag = 'REVIEW'
                )::int AS governance_review_count,
                COUNT(*) FILTER (
                    WHERE governance_flag = 'ESCALATE'
                )::int AS governance_escalation_count,
                COUNT(*) FILTER (
                    WHERE governance_flag = 'SAFE'
                )::int AS governance_safe_count,
                COALESCE(ROUND(AVG(final_score)::numeric, 2), 0)
                    AS average_candidate_score
            FROM applications a
            WHERE {where_sql}
            """
        )

        with engine.connect() as conn:
            row = conn.execute(query, params).mappings().first()

        return dict(row) if row else {}

    @staticmethod
    def get_applications_per_job(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> list[dict[str, Any]]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                COALESCE(j.title, 'Unassigned Role') AS job_title,
                j.id AS job_id,
                COUNT(a.id)::int AS application_count
            FROM applications a
            LEFT JOIN jobs j ON j.id = a.job_id
            WHERE {where_sql}
            GROUP BY j.id, j.title
            ORDER BY application_count DESC, job_title ASC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_governance_distribution(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> list[dict[str, Any]]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                COALESCE(NULLIF(TRIM(governance_flag), ''), 'UNKNOWN')
                    AS governance_flag,
                COUNT(*)::int AS count
            FROM applications a
            WHERE {where_sql}
            GROUP BY 1
            ORDER BY count DESC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_status_distribution(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> list[dict[str, Any]]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                COALESCE(NULLIF(TRIM(application_status), ''), 'PENDING')
                    AS application_status,
                COUNT(*)::int AS count
            FROM applications a
            WHERE {where_sql}
            GROUP BY 1
            ORDER BY count DESC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_score_histogram(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> list[dict[str, Any]]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                CASE
                    WHEN final_score IS NULL THEN 'No Score'
                    WHEN final_score < 0.2 THEN '0.0 - 0.2'
                    WHEN final_score < 0.4 THEN '0.2 - 0.4'
                    WHEN final_score < 0.6 THEN '0.4 - 0.6'
                    WHEN final_score < 0.8 THEN '0.6 - 0.8'
                    ELSE '0.8 - 1.0'
                END AS score_bucket,
                COUNT(*)::int AS count,
                MIN(
                    CASE
                        WHEN final_score IS NULL THEN 99
                        ELSE final_score
                    END
                ) AS sort_key
            FROM applications a
            WHERE {where_sql}
            GROUP BY 1
            ORDER BY sort_key ASC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [
            {
                "score_bucket": row["score_bucket"],
                "count": row["count"],
            }
            for row in rows
        ]

    @staticmethod
    def get_shortlisted_vs_pending(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> list[dict[str, Any]]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                CASE
                    WHEN application_status = 'SHORTLISTED'
                        THEN 'Shortlisted'
                    WHEN COALESCE(application_status, 'PENDING')
                        IN ('PENDING', 'UNDER_REVIEW')
                        THEN 'Pending / Under Review'
                    ELSE 'Other'
                END AS pipeline_stage,
                COUNT(*)::int AS count
            FROM applications a
            WHERE {where_sql}
            GROUP BY 1
            ORDER BY count DESC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_audit_activity_summary(
        start_date=None,
        end_date=None,
    ) -> list[dict[str, Any]]:

        clauses = ["1=1"]
        params: dict[str, Any] = {}

        if start_date is not None:
            clauses.append("DATE(created_at) >= :start_date")
            if isinstance(start_date, datetime):
                params["start_date"] = start_date.date()
            else:
                params["start_date"] = start_date

        if end_date is not None:
            clauses.append("DATE(created_at) <= :end_date")
            if isinstance(end_date, datetime):
                params["end_date"] = end_date.date()
            else:
                params["end_date"] = end_date

        where_sql = " AND ".join(clauses)

        query = text(
            f"""
            SELECT
                COALESCE(NULLIF(TRIM(action_type), ''), 'UNKNOWN')
                    AS action_type,
                COUNT(*)::int AS count
            FROM audit_logs
            WHERE {where_sql}
            GROUP BY 1
            ORDER BY count DESC
            LIMIT 15
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_recruiter_productivity(
        start_date=None,
        end_date=None,
    ) -> list[dict[str, Any]]:

        clauses = ["1=1"]
        params: dict[str, Any] = {}

        if start_date is not None:
            clauses.append("DATE(rf.created_at) >= :start_date")
            if isinstance(start_date, datetime):
                params["start_date"] = start_date.date()
            else:
                params["start_date"] = start_date

        if end_date is not None:
            clauses.append("DATE(rf.created_at) <= :end_date")
            if isinstance(end_date, datetime):
                params["end_date"] = end_date.date()
            else:
                params["end_date"] = end_date

        where_sql = " AND ".join(clauses)

        query = text(
            f"""
            SELECT
                COALESCE(NULLIF(TRIM(recruiter_action), ''), 'UNSPECIFIED')
                    AS recruiter_action,
                COUNT(*)::int AS count
            FROM recruiter_feedback rf
            WHERE {where_sql}
            GROUP BY 1
            ORDER BY count DESC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def get_export_rows(
        start_date=None,
        end_date=None,
        job_id=None,
    ) -> list[dict[str, Any]]:

        where_sql, params = (
            AnalyticsRepository._filter_clause(
                start_date,
                end_date,
                job_id,
            )
        )

        query = text(
            f"""
            SELECT
                a.id AS application_id,
                c.full_name AS candidate_name,
                j.title AS job_title,
                a.application_status,
                a.governance_flag,
                a.final_score,
                a.semantic_score,
                a.keyword_score,
                a.confidence,
                a.created_at
            FROM applications a
            LEFT JOIN candidates c ON c.id = a.candidate_id
            LEFT JOIN jobs j ON j.id = a.job_id
            WHERE {where_sql}
            ORDER BY a.created_at DESC
            """
        )

        with engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()

        return [dict(row) for row in rows]
