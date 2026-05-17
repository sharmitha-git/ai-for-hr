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

# Strict policy signals — queries matching these must NEVER hit recruiter/matching.
POLICY_STRICT_KEYWORDS = [
    "privacy",
    "pii",
    "sensitive data",
    "sensitive information",
    "personal data",
    "gdpr",
    "compliance",
    "regulatory",
    "regulation",
    "security",
    "information security",
    "cybersecurity",
    "audit",
    "retention",
    "encryption",
    "encrypted",
    "policy",
    "protected",
    "data protection",
    "consent",
    "explainability",
    "explainable",
    "fairness",
    "fair hiring",
    "bias",
    "biased",
    "ethics",
    "ethical",
    "lawful basis",
    "data subject",
]

POLICY_STRICT_PHRASES = [
    "what policy",
    "which policy",
    "policy applies",
    "policy require",
    "policy says",
    "according to policy",
    "compliance requirement",
    "privacy policy",
    "governance policy",
    "governance rules",
    "show governance rules",
    "how is candidate data",
    "candidate data stored",
    "data stored",
    "data are stored",
    "is sensitive data",
    "are protected",
    "data protected",
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

RECRUITER_AGENTS = frozenset({
    "recruiter",
    "matching",
})


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


def _collect_policy_signals(lower_query):
    """
    Return matched policy/compliance signals for routing confidence.
    """

    matched = []

    for keyword in POLICY_STRICT_KEYWORDS:

        if keyword in lower_query:

            matched.append(keyword)

    for phrase in POLICY_STRICT_PHRASES:

        if phrase in lower_query:

            matched.append(phrase)

    if (
        "sensitive" in lower_query
        and "data" in lower_query
    ):
        matched.append("sensitive+data")

    if (
        "protected" in lower_query
        and _contains_any(
            lower_query,
            [
                "data",
                "information",
                "pii",
                "personal",
            ],
        )
    ):
        matched.append("data_protected")

    if "governance" in lower_query:

        if not is_governance_analytics_query(lower_query):

            matched.append("governance")

    if "risk" in lower_query:

        if not _contains_any(
            lower_query,
            [
                "audit risk",
                "risk summary",
                "governance risks",
            ],
        ):
            matched.append("risk")

    return list(dict.fromkeys(matched))


def classify_query_intent(query):
    """
    Classify copilot intent with confidence for orchestration logging.
    """

    lower_query = (query or "").lower().strip()

    if not lower_query:

        return {
            "detected_intent": "unknown",
            "confidence": 0.0,
            "matched_signals": [],
            "fallback_reason": "empty_query",
            "force_policy_route": False,
        }

    if is_job_query(query):

        return {
            "detected_intent": "available_jobs",
            "confidence": 0.95,
            "matched_signals": ["job_keywords"],
            "fallback_reason": None,
            "force_policy_route": False,
        }

    if is_governance_analytics_query(lower_query):

        return {
            "detected_intent": "governance_analytics",
            "confidence": 0.92,
            "matched_signals": ["governance_analytics_phrase"],
            "fallback_reason": None,
            "force_policy_route": False,
        }

    policy_signals = _collect_policy_signals(
        lower_query
    )

    if policy_signals:

        confidence = min(
            0.99,
            0.55 + (0.08 * len(policy_signals)),
        )

        return {
            "detected_intent": "policy_compliance",
            "confidence": round(confidence, 3),
            "matched_signals": policy_signals,
            "fallback_reason": None,
            "force_policy_route": True,
        }

    return {
        "detected_intent": "candidate_search",
        "confidence": 0.55,
        "matched_signals": [],
        "fallback_reason": "no_policy_signals_default_recruiter",
        "force_policy_route": False,
    }


def is_policy_compliance_query(query):
    """
    Hard guard: privacy/governance/compliance topics route to policy_agent only.
    """

    return classify_query_intent(
        query
    )["force_policy_route"]


def assert_not_recruiter_for_policy(
    route_plan,
    query,
):
    """
    Hard safety fallback — policy-classified queries must never
    reach recruiter_agent or matching_agent.
    """

    classification = classify_query_intent(
        query
    )

    if not classification["force_policy_route"]:

        return route_plan, classification

    selected = route_plan.get(
        "selected_agent",
        "",
    )

    if selected in RECRUITER_AGENTS:

        policy_plan = _policy_route_plan()
        policy_plan["routing_metadata"] = classification
        policy_plan["routing_metadata"]["fallback_reason"] = (
            "policy_guard_blocked_recruiter_route"
        )
        policy_plan["routing_metadata"]["blocked_route"] = (
            route_plan.get("route_type")
        )

        return policy_plan, classification

    route_plan["routing_metadata"] = classification
    return route_plan, classification


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
        "policy_route_locked": True,
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
    classification = classify_query_intent(query)

    if is_job_query(query):

        plan = {
            "route_type": "available_jobs",
            "selected_agent": "jobs",
            "selected_tool": "get_available_jobs_tool",
            "agent_sequence": ["jobs", "synthesizer"],
            "retrieval_domain": "jobs_db",
            "tool_args": {},
        }
        plan["routing_metadata"] = classification
        return plan

    if classification["force_policy_route"]:

        plan = _policy_route_plan()
        plan["routing_metadata"] = classification
        return plan

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

        plan = {
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
        plan, classification = assert_not_recruiter_for_policy(
            plan,
            query,
        )
        plan["routing_metadata"] = classification
        return plan

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

        plan = {
            "route_type": "shortlisted_candidates",
            "selected_agent": "recruiter",
            "selected_tool": "get_shortlisted_candidates_tool",
            "agent_sequence": ["recruiter", "synthesizer"],
            "retrieval_domain": "applications_db",
            "tool_args": {"job_id": job_id},
        }
        plan, classification = assert_not_recruiter_for_policy(
            plan,
            query,
        )
        plan["routing_metadata"] = classification
        return plan

    if _contains_any(
        lower_query,
        [
            "show pending candidates",
            "pending candidates",
            "who is pending",
        ],
    ):

        plan = {
            "route_type": "pending_candidates",
            "selected_agent": "recruiter",
            "selected_tool": "get_pending_candidates_tool",
            "agent_sequence": ["recruiter", "synthesizer"],
            "retrieval_domain": "applications_db",
            "tool_args": {"job_id": job_id},
        }
        plan, classification = assert_not_recruiter_for_policy(
            plan,
            query,
        )
        plan["routing_metadata"] = classification
        return plan

    if _contains_any(
        lower_query,
        [
            "why was candidate rejected",
            "why rejected",
            "rejected candidate",
            "reason rejected",
        ],
    ):

        plan = {
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
        plan, classification = assert_not_recruiter_for_policy(
            plan,
            query,
        )
        plan["routing_metadata"] = classification
        return plan

    if _contains_any(
        lower_query,
        [
            "summarize hiring pipeline",
            "hiring pipeline",
            "pipeline summary",
        ],
    ):

        plan = {
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
        plan["routing_metadata"] = classification
        return plan

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

        plan = {
            "route_type": "governance_risks",
            "selected_agent": "governance",
            "selected_tool": selected_tool,
            "agent_sequence": ["governance", "synthesizer"],
            "retrieval_domain": "governance_analytics",
            "tool_args": {},
        }
        plan["routing_metadata"] = classification
        return plan

    plan = {
        "route_type": "candidate_search",
        "selected_agent": "recruiter",
        "selected_tool": "semantic_candidate_search",
        "agent_sequence": ["recruiter", "synthesizer"],
        "retrieval_domain": "candidate_vector_search",
        "tool_args": {"job_id": job_id},
    }

    plan, classification = assert_not_recruiter_for_policy(
        plan,
        query,
    )
    plan["routing_metadata"] = classification
    return plan
