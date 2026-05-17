from backend.tools.tool_registry import (
    execute_tool
)
from services.policy_response_service import (
    build_grounded_policy_response,
)
from services.policy_safety_service import (
    check_query_safety,
)


def _advance_to_next_node(state):

    sequence = state.get(
        "agent_sequence",
        []
    )
    current_step = state.get(
        "current_step",
        0
    ) + 1

    state["current_step"] = (
        current_step
    )

    if current_step < len(sequence):

        state["next_agent"] = (
            sequence[current_step]
        )

    else:

        state["next_agent"] = "END"

    return state


def _build_policy_query(state):

    route_type = state.get(
        "route_type"
    )

    if route_type == (
        "rejected_reasoning"
    ):

        recruiter_rows = (
            state.get(
                "agent_outputs",
                {}
            ).get(
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

        role_titles = [
            row.get(
                "role_title"
            )
            for row in recruiter_rows
            if row.get("role_title")
        ]

        if role_titles:

            return (
                "Human review and rejection policy for "
                + ", ".join(
                    role_titles[:3]
                )
            )

    return state.get(
        "query",
        ""
    )


def _log_policy_orchestration(
    orchestration_log,
    policy_output,
    safety_refusal,
):
    """Record route, retrieval metadata, and chunks used."""

    orchestration_log.append(
        "[Policy] selected_route=policy_agent"
    )

    if safety_refusal:

        orchestration_log.append(
            "[Policy] safety_refusal=triggered"
        )
        return orchestration_log

    orchestration_log.append(
        f"[Policy] retrieval_source="
        f"{policy_output.get('retrieval_source', 'none')}"
    )
    orchestration_log.append(
        f"[Policy] retrieval_confidence="
        f"{policy_output.get('retrieval_confidence', 0)}"
    )
    orchestration_log.append(
        f"[Policy] low_confidence="
        f"{policy_output.get('low_confidence', True)}"
    )

    chunks_used = policy_output.get(
        "policy_chunks_used",
        [],
    )

    if chunks_used:

        chunk_summary = ", ".join(
            f"{c.get('source')}:{c.get('confidence', 0):.2f}"
            for c in chunks_used
        )
        orchestration_log.append(
            f"[Policy] policy_chunks_used={chunk_summary}"
        )
    else:

        orchestration_log.append(
            "[Policy] policy_chunks_used=none"
        )

    return orchestration_log


def policy_agent(state):

    user_query = state.get(
        "query",
        ""
    )
    policy_query = _build_policy_query(
        state
    )

    agent_outputs = state.get(
        "agent_outputs",
        {}
    )
    orchestration_log = state.get(
        "orchestration_log",
        []
    )

    is_safe, refusal_message = check_query_safety(
        user_query
    )

    if not is_safe:

        policy_payload = {
            "query": policy_query,
            "data": {
                "results": [],
                "chunks": [],
                "retrieval_source": "safety_refusal",
                "retrieval_confidence": 0.0,
                "low_confidence": True,
                "policy_chunks_used": [],
                "safety_refusal": True,
            },
            "grounded_response": (
                refusal_message
            ),
        }

        orchestration_log = _log_policy_orchestration(
            orchestration_log,
            policy_payload["data"],
            safety_refusal=True,
        )

        agent_outputs["policy"] = policy_payload
        state["agent_outputs"] = agent_outputs
        state["orchestration_log"] = orchestration_log

        return _advance_to_next_node(state)

    try:

        policy_output = execute_tool(
            "search_policy_documents",
            query=policy_query
        )

        orchestration_log.append(
            "[Policy] Executed "
            "search_policy_documents"
        )

    except Exception as exc:

        policy_output = {
            "results": [],
            "chunks": [],
            "error": str(exc),
            "retrieval_source": "policy_faiss",
            "retrieval_confidence": 0.0,
            "low_confidence": True,
            "policy_chunks_used": [],
        }

        orchestration_log.append(
            "[Policy] Fallback triggered "
            "after policy retrieval failure"
        )

    chunks = policy_output.get(
        "chunks",
        [],
    )
    retrieval_confidence = policy_output.get(
        "retrieval_confidence",
        0.0,
    )
    low_confidence = policy_output.get(
        "low_confidence",
        True,
    )

    grounded_response = build_grounded_policy_response(
        user_query,
        chunks,
        retrieval_confidence,
        low_confidence,
    )

    orchestration_log = _log_policy_orchestration(
        orchestration_log,
        policy_output,
        safety_refusal=False,
    )

    agent_outputs["policy"] = {
        "query": policy_query,
        "data": policy_output,
        "grounded_response": grounded_response,
    }
    state["agent_outputs"] = (
        agent_outputs
    )
    state["orchestration_log"] = (
        orchestration_log
    )

    return _advance_to_next_node(
        state
    )
