from backend.tools.tool_registry import (
    register_tool
)


@register_tool(
    "get_escalation_policy"
)
def get_escalation_policy():

    return {

        "workflow": [

            "Candidate evaluated",

            "Low confidence detected",

            "Governance flag assigned",

            "Human recruiter review required",

            "Decision logged in audit system"
        ]
    }