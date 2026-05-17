from backend.tools.tool_registry import (
    register_tool
)

from repositories.candidate_repository import (
    CandidateRepository
)


@register_tool(
    "search_candidates"
)
def search_candidates(
    skills=None
):

    repo = CandidateRepository()

    candidates = (
        repo.get_all_candidates()
    )

    results = []

    for candidate in candidates:

        if (
            skills
            and skills.lower()
            not in candidate.skills.lower()
        ):
            continue

        results.append({

            "candidate_id":
                candidate.id,

            "name":
                candidate.full_name,

            "skills":
                candidate.skills
        })

    return results