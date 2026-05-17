from backend.tools.tool_registry import (
    register_tool
)

from repositories.candidate_repository import (
    CandidateRepository
)


@register_tool(
    "candidate_statistics"
)
def candidate_statistics():

    candidates = (
        CandidateRepository
        .get_all_candidates()
    )

    total = len(candidates)

    shortlisted = 0

    rejected = 0

    reviewing = 0

    for c in candidates:

        status = getattr(
            c,
            "status",
            "review"
        ).lower()

        if status == "shortlisted":

            shortlisted += 1

        elif status == "rejected":

            rejected += 1

        else:

            reviewing += 1

    return {

        "total_candidates":
            total,

        "shortlisted":
            shortlisted,

        "rejected":
            rejected,

        "under_review":
            reviewing
    }