import re

from backend.llm import llm

from backend.tools.tool_registry import (
    execute_tool
)

from memory.conversation_memory import (
    get_memory,
    add_memory
)
from services.policy_rag_service import (
    search_policy_documents
)


def governance_agent(state):

    query = state["query"]

    session_id = state.get(
        "session_id",
        "default"
    )

    memory = get_memory(
        session_id
    )

    lower_query = query.lower()
    policy_evidence = search_policy_documents(
        query
    )

    # -----------------------------------
    # Explain Specific Risk
    # -----------------------------------

    if (
        "application" in lower_query
        and
        (
            "risk" in lower_query
            or
            "risky" in lower_query
        )
    ):

        match = re.search(
            r"\d+",
            query
        )

        if match:

            application_id = int(
                match.group()
            )

            tool_result = execute_tool(

                "explain_governance_risk",

                application_id=application_id
            )

            prompt = f"""

You are a governance compliance AI assistant for a human-in-the-loop hiring platform.

Conversation History:
{memory}

Explain this governance risk
clearly in professional language.

Relevant Policy Evidence:
{policy_evidence}

Rules:
- Never state that AI can make the final hiring decision.
- Explain what a human reviewer should verify next.
- Cite the policy evidence when available.

Data:
{tool_result}

"""

            response = llm.invoke(
                prompt
            )

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
    # Governance Analytics
    # -----------------------------------

    if (
        "statistics" in lower_query
        or
        "analytics" in lower_query
        or
        "summary" in lower_query
    ):

        stats = execute_tool(
            "governance_statistics"
        )

        prompt = f"""

You are a governance analytics AI assistant.

Conversation History:
{memory}

Explain these governance analytics.

Relevant Policy Evidence:
{policy_evidence}

Rules:
- Frame the analytics as decision support only.
- State that any shortlist or rejection requires human review.

Data:
{stats}

"""

        response = llm.invoke(
            prompt
        )

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
    # Default Governance Risks
    # -----------------------------------

    tool_result = execute_tool(
        "get_governance_risks"
    )

    prompt = f"""

You are a governance compliance AI assistant.

Conversation History:
{memory}

Summarize these governance risks.

Relevant Policy Evidence:
{policy_evidence}

Rules:
- Explain why the cases require review.
- State that human approval is mandatory before any final action.

Data:
{tool_result}

"""

    response = llm.invoke(
        prompt
    )

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
