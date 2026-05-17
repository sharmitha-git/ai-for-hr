"""
Copilot query routing (no database dependencies — safe for unit tests).
"""

JOB_KEYWORDS = [
    "jobs available",
    "available jobs",
    "available roles",
    "job roles",
    "open positions",
    "list jobs",
    "list of jobs",
    "what jobs",
    "show jobs",
    "roles available",
]

POLICY_COMPLIANCE_KEYWORDS = [
    "privacy",
    "gdpr",
    "data retention",
    "data protection",
    "personal data",
    "pii",
    "consent",
    "compliance",
    "regulatory",
    "regulation",
    "security policy",
    "information security",
    "cybersecurity",
    "explainability",
    "explainable ai",
    "fairness",
    "fair hiring",
    "bias",
    "biased",
    "ethics",
    "ethical",
    "governance policy",
    "hiring policy",
    "equal opportunity",
    "eeo",
    "retention policy",
    "lawful basis",
    "data subject",
]

POLICY_COMPLIANCE_PHRASES = [
    "what policy",
    "which policy",
    "policy applies",
    "policy require",
    "policy says",
    "according to policy",
    "compliance requirement",
    "compliance policy",
    "privacy policy",
    "governance policy",
]

GOVERNANCE_ANALYTICS_PHRASES = [
    "governance risks",
    "show governance risks",
    "governance analytics",
    "governance summary",
    "risk summary",
    "audit risk",
    "summarize hiring pipeline",
    "hiring pipeline",
    "pipeline summary",
]


def _contains_any(lower_query, phrases):

    return any(
        phrase in lower_query
        for phrase in phrases
    )


def is_job_query(query):

    return _contains_any(
        query.lower().strip(),
        JOB_KEYWORDS,
    )


def is_governance_analytics_query(lower_query):

    return _contains_any(
        lower_query,
        GOVERNANCE_ANALYTICS_PHRASES,
    )


def is_policy_compliance_query(lower_query):
    """
    Privacy / governance / compliance topics must route to policy_agent.
    """

    if is_governance_analytics_query(lower_query):

        return False

    if _contains_any(
        lower_query,
        POLICY_COMPLIANCE_KEYWORDS,
    ):
        return True

    if _contains_any(
        lower_query,
        POLICY_COMPLIANCE_PHRASES,
    ):
        return True

    if "audit" in lower_query:
        return True

    if (
        "governance" in lower_query
        and _contains_any(
            lower_query,
            [
                "policy",
                "privacy",
                "compliance",
                "gdpr",
                "ethics",
                "fairness",
                "bias",
                "security",
                "retention",
            ],
        )
    ):
        return True

    if (
        "security" in lower_query
        and "candidate" not in lower_query
    ):
        return True

    return False


def _policy_route_plan():

    return {
        "route_type": "policy_compliance",
        "selected_agent": "policy",
        "selected_tool": "search_policy_documents",
        "agent_sequence": [
            "policy",
            "synthesizer",
        ],
        "retrieval_domain": "policy_rag",
        "tool_args": {},
    }


def _find_application_for_outreach(query, job_id=None):

    from repositories.application_repository import (
        ApplicationRepository
    )

    rows = (
        ApplicationRepository.get_candidate_decision_details(
            job_id=job_id
        )
    )

    lower_query = (query or "").lower()

    for row in rows:

        candidate_name = row.get(
            "candidate_name",
            "",
        ).lower()

        if candidate_name and candidate_name in lower_query:

            return row

    if _contains_any(
        lower_query,
        ["shortlisted", "interview", "outreach"],
    ):

        for row in rows:

            if row.get(
                "application_status"
            ) == "SHORTLISTED":

                return row

    return rows[0] if rows else None


def build_route_plan(query, job_id=None):

    lower_query = (query or "").lower()

    if is_job_query(query):

        return {
            "route_type": "available_jobs",
            "selected_agent": "jobs",
            "selected_tool": "get_available_jobs_tool",
            "agent_sequence": ["jobs", "synthesizer"],
            "retrieval_domain": "jobs_db",
            "tool_args": {},
        }

    if is_policy_compliance_query(lower_query):

        return _policy_route_plan()

    if _contains_any(
        lower_query,
        [
            "email shortlisted candidates",
            "email shortlisted",
            "send interview email",
            "draft outreach mail",
            "notify shortlisted applicants",
            "notify shortlisted",
            "draft interview invite",
            "generate rejection email",
            "prepare outreach",
        ],
    ):

        target_application = _find_application_for_outreach(
            query,
            job_id,
        )

        email_type = (
            "REJECTION"
            if "rejection" in lower_query
            else "INTERVIEW_INVITE"
        )

        return {
            "route_type": "email_outreach",
            "selected_agent": "outreach",
            "selected_tool": "generate_email_draft_tool",
            "agent_sequence": [
                "outreach",
                "governance",
                "synthesizer",
            ],
            "retrieval_domain": "outreach_db",
            "tool_args": {
                "application_id": (
                    target_application.get("application_id")
                    if target_application
                    else None
                ),
                "email_type": email_type,
            },
        }

    if _contains_any(
        lower_query,
        [
            "who are shortlisted",
            "who is shortlisted",
            "name shortlisted candidates",
            "show shortlisted candidates",
            "shortlisted candidates",
        ],
    ):

        return {
            "route_type": "shortlisted_candidates",
            "selected_agent": "recruiter",
            "selected_tool": "get_shortlisted_candidates_tool",
            "agent_sequence": ["recruiter", "synthesizer"],
            "retrieval_domain": "applications_db",
            "tool_args": {"job_id": job_id},
        }

    if _contains_any(
        lower_query,
        [
            "show pending candidates",
            "pending candidates",
            "who is pending",
        ],
    ):

        return {
            "route_type": "pending_candidates",
            "selected_agent": "recruiter",
            "selected_tool": "get_pending_candidates_tool",
            "agent_sequence": ["recruiter", "synthesizer"],
            "retrieval_domain": "applications_db",
            "tool_args": {"job_id": job_id},
        }

    if _contains_any(
        lower_query,
        [
            "why was candidate rejected",
            "why rejected",
            "rejected candidate",
            "reason rejected",
        ],
    ):

        return {
            "route_type": "rejected_reasoning",
            "selected_agent": "recruiter",
            "selected_tool": "get_rejected_candidates_tool",
            "agent_sequence": [
                "recruiter",
                "governance",
                "policy",
                "synthesizer",
            ],
            "retrieval_domain": "applications_db",
            "tool_args": {"job_id": job_id},
        }

    if _contains_any(
        lower_query,
        [
            "summarize hiring pipeline",
            "hiring pipeline",
            "pipeline summary",
        ],
    ):

        return {
            "route_type": "pipeline_summary",
            "selected_agent": "governance",
            "selected_tool": "governance_statistics",
            "agent_sequence": [
                "governance",
                "operations",
                "synthesizer",
            ],
            "retrieval_domain": "governance_analytics",
            "tool_args": {},
        }

    if _contains_any(
        lower_query,
        [
            "governance risks",
            "show governance risks",
            "governance analytics",
            "governance summary",
            "risk summary",
            "audit risk",
        ],
    ):

        selected_tool = (
            "governance_statistics"
            if _contains_any(
                lower_query,
                ["analytics", "statistics", "summary"],
            )
            else "get_governance_risks"
        )

        return {
            "route_type": "governance_risks",
            "selected_agent": "governance",
            "selected_tool": selected_tool,
            "agent_sequence": ["governance", "synthesizer"],
            "retrieval_domain": "governance_analytics",
            "tool_args": {},
        }

    return {
        "route_type": "candidate_search",
        "selected_agent": "recruiter",
        "selected_tool": "semantic_candidate_search",
        "agent_sequence": ["recruiter", "synthesizer"],
        "retrieval_domain": "candidate_vector_search",
        "tool_args": {"job_id": job_id},
    }
