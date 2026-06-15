from langchain_core.messages import (
    HumanMessage
)

from backend.routing.copilot_router import (
    is_policy_compliance_query,
)
from backend.tools.semantic_search_tool import (
    semantic_candidate_search
)

from backend.tools.tool_registry import (
    execute_tool
)

from memory.conversation_memory import (
    get_memory,
    add_memory
)

from backend.llm import llm


def recruiter_agent(state):

    query = state["query"]

    if is_policy_compliance_query(
        query
    ):

        state["response"] = (
            "No grounded policy information found. "
            "This query was blocked from recruiter flow."
        )
        state["message"] = state["response"]
        return state

    lower_query = query.lower()

    session_id = state.get(
        "session_id",
        "default"
    )

    memory = get_memory(
        session_id
    )

    # -----------------------------------
    # Recruitment Analytics
    # -----------------------------------

    if (
        "how many" in lower_query
        or
        "count" in lower_query
        or
        "shortlisted" in lower_query
        or
        "rejected" in lower_query
    ):

        stats = execute_tool(
            "candidate_statistics"
        )

        prompt = f"""

You are an AI recruitment analytics assistant.

Conversation History:
{memory}

User Query:
{query}

Analytics Data:
{stats}

Answer naturally and professionally.

"""

        response = llm.invoke([

            HumanMessage(
                content=prompt
            )

        ])

        response_text = (
            response.content
        )

        add_memory(
            session_id,
            "user",
            query
        )

        add_memory(
            session_id,
            "assistant",
            response_text
        )

        state["response"] = (
            response_text
        )

        return state

    # -----------------------------------
    # Semantic Candidate Search
    # -----------------------------------

    candidates = (
        semantic_candidate_search(
            query
        )
    )

    prompt = f"""

You are an AI recruiter assistant for a human-in-the-loop hiring platform.

Conversation History:
{memory}

User Query:
{query}

Retrieved Candidates:
{candidates}

Rules:

- Do not autonomously hire, reject, shortlist, or finalize decisions.
- Treat all outputs as advisory decision support for a human recruiter.
- Be explicit about evidence, uncertainty, and missing information.

Explain naturally:

- who is strongest
- why they match
- important skills
- risks or gaps
- what the human recruiter should review next
- end with a short statement that human approval is required

"""

    response = llm.invoke([

        HumanMessage(
            content=prompt
        )

    ])

    response_text = (
        response.content
    )

    add_memory(
        session_id,
        "user",
        query
    )

    add_memory(
        session_id,
        "assistant",
        response_text
    )

    state["candidates"] = (
        candidates
    )

    state["response"] = (
        response_text
    )

    return state
