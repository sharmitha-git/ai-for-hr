from backend.tools.tool_registry import (
    register_tool
)


@register_tool(
    "send_shortlist_email"
)
def send_shortlist_email(
    candidate_email
):

    return {

        "status":
            "email_sent",

        "recipient":
            candidate_email,

        "template":
            "shortlist_notification"
    }


@register_tool(
    "send_rejection_email"
)
def send_rejection_email(
    candidate_email
):

    return {

        "status":
            "email_sent",

        "recipient":
            candidate_email,

        "template":
            "rejection_notification"
    }