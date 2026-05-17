from backend.llm import llm
from backend.routing.copilot_router import (
    is_policy_compliance_query,
)
from memory.conversation_memory import (
    MEMORY_SCOPE_CANDIDATE_MATCHING,
    add_memory,
    resolve_memory_scope
)

from repositories.candidate_repository import (
    CandidateRepository
)


def matching_agent(state):

    query = state["query"]

    if is_policy_compliance_query(
        query
    ):

        state["response"] = (
            "No grounded policy information found. "
            "This query must be handled by the policy agent."
        )
        return state

    # Scoped string from supervisor; never mix with other route partitions.
    memory = state.get(
        "memory",
        ""
    )
    memory_scope = state.get(
        "memory_scope",
        MEMORY_SCOPE_CANDIDATE_MATCHING
    ) or resolve_memory_scope(
        state.get("route_type")
    )

    candidates = (
        CandidateRepository
        .get_all_candidates()
    )

    candidate_text = ""

    for c in candidates:

        candidate_text += f"""

Name: {c.full_name}
Skills: {c.skills}

"""

    prompt = f"""

You are an AI hiring matching assistant.

Conversation History:
{memory}

User Request:
{query}

Candidates:
{candidate_text}

Find the best matching candidates
and explain why they match.

"""

    response = llm.invoke(
        prompt
    )

    response_text = (
        response.content
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

    state["memory"] = memory

    state["response"] = (
        response_text
    )

    state["candidates"] = (
        candidates
    )

    return state