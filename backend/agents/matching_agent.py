from backend.llm import llm

from repositories.candidate_repository import (
    CandidateRepository
)


def matching_agent(state):

    query = state["query"]

    memory = state.get(
        "memory",
        []
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

    memory.append(
        f"User: {query}"
    )

    memory.append(
        f"Assistant: {response_text}"
    )

    state["memory"] = memory

    state["response"] = (
        response_text
    )

    state["candidates"] = (
        candidates
    )

    return state