from memory.conversation_memory import (
    add_memory,
    get_memory,
    resolve_memory_scope
)
from repositories.application_repository import (
    ApplicationRepository
)


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


def _contains_any(
    lower_query,
    phrases
):

    return any(
        phrase in lower_query
        for phrase in phrases
    )


def _is_job_query(query):

    normalized_query = (
        query.lower().strip()
    )

    return _contains_any(
        normalized_query,
        JOB_KEYWORDS
    )


def _find_application_for_outreach(
    query,
    job_id=None
):

    rows = (
        ApplicationRepository
        .get_candidate_decision_details(
            job_id=job_id
        )
    )

    lower_query = (
        query or ""
    ).lower()

    for row in rows:

        candidate_name = (
            row.get(
                "candidate_name",
                ""
            ).lower()
        )

        if candidate_name and candidate_name in lower_query:

            return row

    if _contains_any(
        lower_query,
        [
            "shortlisted",
            "interview",
            "outreach"
        ]
    ):

        for row in rows:

            if row.get(
                "application_status"
            ) == "SHORTLISTED":

                return row

    return rows[0] if rows else None


def _build_route_plan(
    query,
    job_id=None
):

    lower_query = (
        query or ""
    ).lower()

    if _is_job_query(query):

        return {
            "route_type":
                "available_jobs",
            "selected_agent":
                "jobs",
            "selected_tool":
                "get_available_jobs_tool",
            "agent_sequence": [
                "jobs",
                "synthesizer"
            ],
            "retrieval_domain":
                "jobs_db",
            "tool_args": {}
        }

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
            "prepare outreach"
        ]
    ):

        target_application = (
            _find_application_for_outreach(
                query,
                job_id
            )
        )

        email_type = (
            "REJECTION"
            if "rejection" in lower_query
            else "INTERVIEW_INVITE"
        )

        return {
            "route_type":
                "email_outreach",
            "selected_agent":
                "outreach",
            "selected_tool":
                "generate_email_draft_tool",
            "agent_sequence": [
                "outreach",
                "governance",
                "synthesizer"
            ],
            "retrieval_domain":
                "outreach_db",
            "tool_args": {
                "application_id": (
                    target_application.get(
                        "application_id"
                    )
                    if target_application else None
                ),
                "email_type": email_type
            }
        }


    if _contains_any(
        lower_query,
        [
            "who are shortlisted",
            "who is shortlisted",
            "name shortlisted candidates",
            "show shortlisted candidates",
            "shortlisted candidates"
        ]
    ):

        return {
            "route_type":
                "shortlisted_candidates",
            "selected_agent":
                "recruiter",
            "selected_tool":
                "get_shortlisted_candidates_tool",
            "agent_sequence": [
                "recruiter",
                "synthesizer"
            ],
            "retrieval_domain":
                "applications_db",
            "tool_args": {
                "job_id": job_id
            }
        }

    if _contains_any(
        lower_query,
        [
            "show pending candidates",
            "pending candidates",
            "who is pending"
        ]
    ):

        return {
            "route_type":
                "pending_candidates",
            "selected_agent":
                "recruiter",
            "selected_tool":
                "get_pending_candidates_tool",
            "agent_sequence": [
                "recruiter",
                "synthesizer"
            ],
            "retrieval_domain":
                "applications_db",
            "tool_args": {
                "job_id": job_id
            }
        }

    if _contains_any(
        lower_query,
        [
            "why was candidate rejected",
            "why rejected",
            "rejected candidate",
            "reason rejected"
        ]
    ):

        return {
            "route_type":
                "rejected_reasoning",
            "selected_agent":
                "recruiter",
            "selected_tool":
                "get_rejected_candidates_tool",
            "agent_sequence": [
                "recruiter",
                "governance",
                "policy",
                "synthesizer"
            ],
            "retrieval_domain":
                "applications_db",
            "tool_args": {
                "job_id": job_id
            }
        }

    if _contains_any(
        lower_query,
        [
            "policy applies",
            "what policy applies",
            "policy",
            "compliance"
        ]
    ):

        return {
            "route_type":
                "policy_lookup",
            "selected_agent":
                "policy",
            "selected_tool":
                "search_policy_documents",
            "agent_sequence": [
                "policy",
                "synthesizer"
            ],
            "retrieval_domain":
                "policy_rag",
            "tool_args": {}
        }

    if _contains_any(
        lower_query,
        [
            "summarize hiring pipeline",
            "hiring pipeline",
            "pipeline summary"
        ]
    ):

        return {
            "route_type":
                "pipeline_summary",
            "selected_agent":
                "governance",
            "selected_tool":
                "governance_statistics",
            "agent_sequence": [
                "governance",
                "operations",
                "synthesizer"
            ],
            "retrieval_domain":
                "governance_analytics",
            "tool_args": {}
        }

    if _contains_any(
        lower_query,
        [
            "governance risks",
            "show governance risks",
            "governance analytics",
            "governance summary",
            "risk summary",
            "audit risk"
        ]
    ):

        selected_tool = (
            "governance_statistics"
            if _contains_any(
                lower_query,
                [
                    "analytics",
                    "statistics",
                    "summary"
                ]
            )
            else "get_governance_risks"
        )

        return {
            "route_type":
                "governance_risks",
            "selected_agent":
                "governance",
            "selected_tool":
                selected_tool,
            "agent_sequence": [
                "governance",
                "synthesizer"
            ],
            "retrieval_domain":
                "governance_analytics",
            "tool_args": {}
        }

    return {
        "route_type":
            "candidate_search",
        "selected_agent":
            "recruiter",
        "selected_tool":
            "semantic_candidate_search",
        "agent_sequence": [
            "recruiter",
            "synthesizer"
        ],
        "retrieval_domain":
            "candidate_vector_search",
        "tool_args": {
            "job_id": job_id
        }
    }


def supervisor_agent(state):

    query = state.get(
        "query",
        ""
    )

    session_id = state.get(
        "session_id",
        "default_user"
    )

    job_id = state.get(
        "job_id"
    )

    route_plan = _build_route_plan(
        query,
        job_id
    )

    state["selected_agent"] = (
        route_plan[
            "selected_agent"
        ]
    )
    state["selected_tool"] = (
        route_plan[
            "selected_tool"
        ]
    )
    state["route_type"] = (
        route_plan["route_type"]
    )
    state["retrieval_domain"] = (
        route_plan[
            "retrieval_domain"
        ]
    )
    state["tool_args"] = (
        route_plan.get(
            "tool_args",
            {}
        )
    )
    state["agent_sequence"] = (
        route_plan[
            "agent_sequence"
        ]
    )
    state["current_step"] = 0
    state["next_agent"] = (
        route_plan[
            "agent_sequence"
        ][0]
    )

    # Load only history for this route's memory partition (e.g. jobs vs candidates).
    memory_scope = resolve_memory_scope(
        route_plan["route_type"]
    )
    state["memory_scope"] = memory_scope
    state["memory"] = get_memory(
        session_id,
        memory_scope
    )
    state["agent_outputs"] = {}

    orchestration_log = state.get(
        "orchestration_log",
        []
    )
    orchestration_log.append(
        f"[Supervisor] Routed to "
        f"{state['selected_agent']}_agent"
    )
    orchestration_log.append(
        f"[Supervisor] Selected tool "
        f"{state['selected_tool']}"
    )
    state["orchestration_log"] = (
        orchestration_log
    )

    add_memory(
        session_id,
        "user",
        query,
        memory_scope
    )

    return state
