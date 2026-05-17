from backend.routing.copilot_router import (
    build_route_plan,
)
from memory.conversation_memory import (
    add_memory,
    get_memory,
    resolve_memory_scope,
)


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

    route_plan = build_route_plan(
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

    memory_scope = resolve_memory_scope(
        route_plan["route_type"]
    )
    state["memory_scope"] = memory_scope
    state["memory"] = get_memory(
        session_id,
        memory_scope
    )
    state["agent_outputs"] = {}

    routing_metadata = route_plan.get(
        "routing_metadata",
        {},
    )

    orchestration_log = state.get(
        "orchestration_log",
        []
    )
    orchestration_log.append(
        f"[Supervisor] detected_intent="
        f"{routing_metadata.get('detected_intent', 'unknown')}"
    )
    orchestration_log.append(
        f"[Supervisor] route_confidence="
        f"{routing_metadata.get('confidence', 0)}"
    )
    orchestration_log.append(
        f"[Supervisor] matched_signals="
        f"{routing_metadata.get('matched_signals', [])}"
    )
    fallback_reason = routing_metadata.get(
        "fallback_reason"
    )
    if fallback_reason:

        orchestration_log.append(
            f"[Supervisor] fallback_reason={fallback_reason}"
        )
    if routing_metadata.get(
        "blocked_route"
    ):

        orchestration_log.append(
            f"[Supervisor] policy_guard_blocked="
            f"{routing_metadata.get('blocked_route')}"
        )
    orchestration_log.append(
        f"[Supervisor] route_type="
        f"{route_plan['route_type']}"
    )
    orchestration_log.append(
        f"[Supervisor] selected_route="
        f"{state['selected_agent']}_agent"
    )
    orchestration_log.append(
        f"[Supervisor] retrieval_domain="
        f"{state['retrieval_domain']}"
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
