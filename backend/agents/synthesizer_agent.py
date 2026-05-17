from backend.llm import llm
from memory.conversation_memory import (
    add_memory,
    resolve_memory_scope
)


def _filter_rows_by_query_name(
    rows,
    query
):

    lower_query = (
        query or ""
    ).lower()

    matched_rows = [
        row for row in rows
        if row.get(
            "candidate_name",
            ""
        ).lower() in lower_query
    ]

    return matched_rows or rows


def _format_jobs(agent_outputs):

    try:

        jobs = (
            agent_outputs.get(
                "jobs",
                {}
            ).get(
                "data",
                {}
            ).get(
                "jobs",
                []
            )
        )

        if not jobs:
            return (
                "# Available Job Roles\n\n"
                "No job roles are currently available."
            )
        lines = ["# Available Job Roles\n"]

        for index, job in enumerate(
            jobs,
            start=1
        ):

            title = job.get(
                'title',
                'Untitled Role'
            )
            required_skills = job.get(
                'required_skills',
                'Not specified'
            )
            applicant_count = job.get(
                'applicant_count',
                0
            )
            shortlisted_count = job.get(
                'shortlisted_count',
                0
            )
            lines.append("")
            lines.append(f"{index}. {title}")
            lines.append(
                f"   - Required Skills: {required_skills}"
            )
            lines.append(
                f"   - Applicants: {applicant_count}"
            )
            lines.append(
                f"   - Shortlisted: {shortlisted_count}"
            )

        return "\n".join(lines).strip()

    except Exception as exc:

        return (
            "# Available Job Roles\n\n"
            f"Error retrieving job listings: {str(exc)}"
        )


def _format_shortlisted(agent_outputs):

    candidates = (
        agent_outputs.get(
            "recruiter",
            {}
        ).get(
            "data",
            {}
        ).get(
            "shortlisted_candidates",
            []
        )
    )

    if not candidates:

        return (
            "Shortlisted Candidates:\n\n"
            "No shortlisted candidates found."
        )

    lines = [
        "Shortlisted Candidates:\n"
    ]

    for index, row in enumerate(
        candidates,
        start=1
    ):

        lines.append(
            f"{index}. "
            f"{row.get('candidate_name', 'Unknown Candidate')}"
        )
        lines.append(
            f"- Role: "
            f"{row.get('role_title', 'Unknown Role')}"
        )
        lines.append(
            f"- Final Score: "
            f"{row.get('final_score', 'N/A')}"
        )
        lines.append(
            f"- Governance Flag: "
            f"{row.get('governance_flag', 'N/A')}"
        )
        lines.append(
            f"- Confidence Score: "
            f"{row.get('confidence_score', 'N/A')}"
        )
        lines.append("")

    return "\n".join(lines).strip()


def _format_pending(agent_outputs):

    candidates = (
        agent_outputs.get(
            "recruiter",
            {}
        ).get(
            "data",
            {}
        ).get(
            "pending_candidates",
            []
        )
    )

    if not candidates:

        return (
            "Pending Candidates:\n\n"
            "No pending candidates found."
        )

    lines = [
        "Pending Candidates:\n"
    ]

    for index, row in enumerate(
        candidates,
        start=1
    ):

        lines.append(
            f"{index}. "
            f"{row.get('candidate_name', 'Unknown Candidate')}"
        )
        lines.append(
            f"- Role: "
            f"{row.get('role_title', 'Unknown Role')}"
        )
        lines.append(
            f"- Application Status: "
            f"{row.get('application_status', 'PENDING')}"
        )
        lines.append(
            f"- Governance Flag: "
            f"{row.get('governance_flag', 'N/A')}"
        )
        lines.append("")

    return "\n".join(lines).strip()


def _format_email_outreach(agent_outputs):

    outreach_data = (
        agent_outputs.get(
            "outreach",
            {}
        ).get(
            "data",
            {}
        )
    )

    draft = outreach_data.get(
        "email_draft"
    )

    if not draft:

        return (
            "Email Outreach Draft:\n\n"
            "No email draft could be generated from the current database records."
        )

    governance_message = (
        agent_outputs.get(
            "governance",
            {}
        ).get(
            "data",
            {}
        ).get(
            "message",
            "Human approval required before any outreach."
        )
    )

    return (
        "Email Outreach Draft:\n\n"
        f"Candidate: {draft.get('candidate_name')}\n"
        f"Role: {draft.get('role_title')}\n"
        f"Draft Status: {draft.get('status')}\n"
        f"Subject: {draft.get('subject')}\n\n"
        f"{draft.get('body')}\n\n"
        f"{governance_message}"
    )


def _format_governance_risks(agent_outputs):

    data = (
        agent_outputs.get(
            "governance",
            {}
        ).get(
            "data",
            {}
        )
    )

    risky_candidates = data.get(
        "risky_candidates",
        []
    )

    if "review_count" in data:

        return (
            "Governance Summary:\n\n"
            f"- Total Applications: {data.get('total_applications', 0)}\n"
            f"- SAFE: {data.get('safe_count', 0)}\n"
            f"- REVIEW: {data.get('review_count', 0)}\n"
            f"- ESCALATE: {data.get('escalate_count', 0)}\n"
            f"- SHORTLISTED: {data.get('shortlisted_count', 0)}\n"
            f"- REJECTED: {data.get('rejected_count', 0)}\n"
            f"- PENDING/UNDER_REVIEW: {data.get('under_review_count', 0)}\n"
            f"- Average Score: {data.get('average_score', 0)}"
        )

    if not risky_candidates:

        return (
            "Governance Risks:\n\n"
            "No applications are currently flagged "
            "for governance review."
        )

    lines = ["Governance Risks:\n"]

    for index, row in enumerate(
        risky_candidates,
        start=1
    ):

        lines.append(
            f"{index}. "
            f"{row.get('candidate_name', 'Unknown Candidate')}"
        )
        lines.append(
            f"- Role: "
            f"{row.get('role_title', 'Unknown Role')}"
        )
        lines.append(
            f"- Governance Flag: "
            f"{row.get('governance_flag', 'N/A')}"
        )
        lines.append(
            f"- Application Status: "
            f"{row.get('application_status', 'N/A')}"
        )
        lines.append(
            f"- Final Score: "
            f"{row.get('final_score', 'N/A')}"
        )
        lines.append("")

    return "\n".join(lines).strip()


def _format_policy(agent_outputs):

    results = (
        agent_outputs.get(
            "policy",
            {}
        ).get(
            "data",
            {}
        ).get(
            "results",
            []
        )
    )

    if not results:

        return (
            "Applicable Policy Guidance:\n\n"
            "No indexed policy snippets were found. "
            "Upload governance PDFs and run policy indexing."
        )

    lines = [
        "Applicable Policy Guidance:\n"
    ]

    for index, snippet in enumerate(
        results,
        start=1
    ):

        lines.append(
            f"{index}. {snippet}"
        )
        lines.append("")

    return "\n".join(lines).strip()


def _format_rejected_reasoning(agent_outputs):

    query = (
        agent_outputs.get(
            "recruiter",
            {}
        ).get(
            "query",
            ""
        )
    )

    recruiter_rows = (
        agent_outputs.get(
            "recruiter",
            {}
        ).get(
            "data",
            {}
        ).get(
            "rejected_candidates",
            []
        )
    )

    governance_rows = (
        agent_outputs.get(
            "governance",
            {}
        ).get(
            "data",
            {}
        ).get(
            "rejected_candidates",
            []
        )
    )

    recruiter_rows = _filter_rows_by_query_name(
        recruiter_rows,
        query
    )
    governance_rows = _filter_rows_by_query_name(
        governance_rows,
        query
    )

    policy_results = (
        agent_outputs.get(
            "policy",
            {}
        ).get(
            "data",
            {}
        ).get(
            "results",
            []
        )
    )

    if not recruiter_rows:

        return (
            "Rejected Candidates:\n\n"
            "No rejected candidates were found."
        )

    lines = ["Rejected Candidate Review:\n"]

    for index, row in enumerate(
        governance_rows or recruiter_rows,
        start=1
    ):

        latest_feedback = (
            row.get(
                "feedback_history",
                []
            )[0]
            if row.get(
                "feedback_history",
                []
            ) else {}
        )

        lines.append(
            f"{index}. "
            f"{row.get('candidate_name', 'Unknown Candidate')}"
        )
        lines.append(
            f"- Role: "
            f"{row.get('role_title', 'Unknown Role')}"
        )
        lines.append(
            f"- Governance Flag: "
            f"{row.get('governance_flag', 'N/A')}"
        )
        lines.append(
            f"- Final Score: "
            f"{row.get('final_score', 'N/A')}"
        )
        lines.append(
            f"- Confidence Score: "
            f"{row.get('confidence_score', 'N/A')}"
        )
        lines.append(
            f"- Recruiter Feedback: "
            f"{latest_feedback.get('recruiter_notes', 'No recruiter notes recorded')}"
        )
        if row.get(
            "governance_explanation"
        ):
            lines.append(
                f"- Governance Explanation: "
                f"{row.get('governance_explanation')}"
            )
        lines.append("")

    if policy_results:

        lines.append(
            "Relevant Policy Guidance:"
        )

        for snippet in policy_results[:3]:

            lines.append(
                f"- {snippet}"
            )

    return "\n".join(lines).strip()


def _format_pipeline_summary(agent_outputs):

    governance_data = (
        agent_outputs.get(
            "governance",
            {}
        ).get(
            "data",
            {}
        )
    )

    workflow = (
        agent_outputs.get(
            "operations",
            {}
        ).get(
            "workflow",
            {}
        ).get(
            "workflow",
            []
        )
    )

    lines = [
        "Hiring Pipeline Summary:\n",
        f"- Total Applications: {governance_data.get('total_applications', 0)}",
        f"- SAFE: {governance_data.get('safe_count', 0)}",
        f"- REVIEW: {governance_data.get('review_count', 0)}",
        f"- ESCALATE: {governance_data.get('escalate_count', 0)}",
        f"- SHORTLISTED: {governance_data.get('shortlisted_count', 0)}",
        f"- REJECTED: {governance_data.get('rejected_count', 0)}",
        f"- PENDING/UNDER_REVIEW: {governance_data.get('under_review_count', 0)}",
        "",
        "Escalation Workflow:"
    ]

    for step in workflow:

        lines.append(
            f"- {step}"
        )

    return "\n".join(lines).strip()


def _format_candidate_search(state):

    candidates = state.get(
        "candidates",
        []
    )

    if not candidates:

        return (
            "Candidate Search Results:\n\n"
            "No matching candidates were found."
        )

    memory = state.get(
        "memory",
        ""
    )

    history_block = ""
    if memory:
        history_block = f"""
    Conversation History (candidate matching only):
    {memory}
    """

    prompt = f"""
    You are a recruiter copilot.

    Use ONLY the retrieved candidate data below.
    Do not invent job roles or policy details.
    Do not mention any candidate not present in the data.
    {history_block}
    User Query:
    {state.get('query', '')}

    Retrieved Candidates:
    {candidates}

    Required structure:
    1. Strongest candidate
    2. Matching skills
    3. Reasoning
    4. Recommendation
    5. A final note that human approval is required
    """

    try:

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception:

        top_candidate = candidates[0]

        return (
            "Candidate Search Results:\n\n"
            f"Strongest candidate: {top_candidate.get('full_name', 'Unknown Candidate')}\n"
            f"Skills: {top_candidate.get('skills', 'Not listed')}\n"
            f"Reasoning: this candidate ranked highest in semantic search for the request.\n"
            f"Recommendation: review this candidate manually before any final hiring action.\n"
            "Human approval is required before shortlist or rejection."
        )


def synthesizer_agent(state):

    route_type = state.get(
        "route_type"
    )
    selected_agent = state.get(
        "selected_agent"
    )
    agent_outputs = state.get(
        "agent_outputs",
        {}
    )

    if (
        selected_agent == "jobs"
        or route_type == "available_jobs"
    ):

        response_text = _format_jobs(
            agent_outputs
        )
        state["response"] = response_text
        state["final_response"] = response_text
        state["message"] = response_text

    elif route_type == (
        "shortlisted_candidates"
    ):

        response_text = _format_shortlisted(
            agent_outputs
        )

    elif route_type == (
        "pending_candidates"
    ):

        response_text = _format_pending(
            agent_outputs
        )

    elif route_type == (
        "governance_risks"
    ):

        response_text = (
            _format_governance_risks(
                agent_outputs
            )
        )

    elif route_type == (
        "policy_lookup"
    ):

        response_text = _format_policy(
            agent_outputs
        )

    elif route_type == (
        "rejected_reasoning"
    ):

        response_text = (
            _format_rejected_reasoning(
                agent_outputs
            )
        )

    elif route_type == (
        "pipeline_summary"
    ):

        response_text = (
            _format_pipeline_summary(
                agent_outputs
            )
        )

    elif route_type == (
        "email_outreach"
    ):

        response_text = (
            _format_email_outreach(
                agent_outputs
            )
        )

    else:

        response_text = (
            _format_candidate_search(
                state
            )
        )

    # Persist assistant output under the same scope as the user turn.
    memory_scope = state.get(
        "memory_scope"
    ) or resolve_memory_scope(
        route_type
    )
    add_memory(
        state.get(
            "session_id",
            "default_user"
        ),
        "assistant",
        response_text,
        memory_scope
    )
    print("FINAL RESPONSE TEXT:", response_text)
          
    state["response"] = (
        response_text
    )
    state["final_response"] = (
        response_text
    )
    state["message"] = (
        response_text
    )

    orchestration_log = state.get(
        "orchestration_log",
        []
    )
    orchestration_log.append(
        f"[Synthesizer] selected_agent={selected_agent}"
    )
    orchestration_log.append(
        f"[Synthesizer] route_type={route_type}"
    )
    response_key = [
        key for key in ["response", "final_response", "message"]
        if key in state 
    ]
    orchestration_log.append(
        f"[Synthesizer] response keys={response_key}"
    )
    state["orchestration_log"] = (
        orchestration_log
    )
    state["next_agent"] = "END"

    return state
