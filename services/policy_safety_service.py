"""
Safety checks for policy / governance copilot queries.
"""

import re
from typing import Tuple


UNSAFE_PATTERNS = [
    (
        re.compile(
            r"\b(discriminat\w*|only hire (men|women)|reject (all )?(black|white|asian|hispanic|muslim|jewish))\b",
            re.I,
        ),
        "HireGuard cannot assist with discriminatory hiring requests. "
        "All hiring decisions must follow equal-opportunity and "
        "documented governance policies with human review.",
    ),
    (
        re.compile(
            r"\b(show|list|dump|export|reveal|give me)\b.{0,40}\b(ssn|social security|passport|home address|personal phone|salary history)\b",
            re.I,
        ),
        "HireGuard cannot expose candidate PII. "
        "Use masked resume data and approved audit channels only.",
    ),
    (
        re.compile(
            r"\b(auto[- ]?reject|auto[- ]?hire|hire without (review|approval)|fully automated hiring decision)\b",
            re.I,
        ),
        "Automated hiring decisions without human approval are not permitted. "
        "Final shortlist, rejection, and outreach require human-in-the-loop review.",
    ),
    (
        re.compile(
            r"\b(rank|select|shortlist|prefer)\b.{0,30}\b(based on (race|gender|age|religion|nationality)|biased|unfair)\b",
            re.I,
        ),
        "HireGuard cannot support biased candidate selection. "
        "Use skill-based evaluation and governance-reviewed criteria only.",
    ),
]


def check_query_safety(
    query: str,
) -> Tuple[bool, str | None]:
    """
    Returns (is_safe, refusal_message).
    refusal_message is set when is_safe is False.
    """

    normalized = (query or "").strip()

    if not normalized:

        return True, None

    for pattern, refusal in UNSAFE_PATTERNS:

        if pattern.search(normalized):

            return False, refusal

    return True, None
