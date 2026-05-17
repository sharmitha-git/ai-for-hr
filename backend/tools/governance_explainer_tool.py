from backend.tools.tool_registry import (
    register_tool
)

from database.connection import SessionLocal

from backend.entities import Application


# -----------------------------------
# Governance Summary Tool
# -----------------------------------

@register_tool(
    "get_governance_risks"
)
def get_governance_risks():

    db = SessionLocal()

    risky = db.query(
        Application
    ).filter(

        Application.governance_flag
        == "REVIEW"

    ).all()

    results = []

    for row in risky:

        results.append({

            "application_id":
                row.id,

            "governance_flag":
                row.governance_flag,

            "confidence_score":
                row.confidence_score,

            "final_score":
                row.final_score
        })

    db.close()

    return {

        "total_risky":
            len(results),

        "risky_candidates":
            results
    }


# -----------------------------------
# Single Application Risk Explainer
# -----------------------------------

@register_tool(
    "explain_governance_risk"
)
def explain_governance_risk(
    application_id
):

    db = SessionLocal()

    application = db.query(
        Application
    ).filter(

        Application.id
        == application_id

    ).first()

    if not application:

        db.close()

        return (
            f"Application {application_id} not found"
        )

    explanation = f"""

Application {application.id} was flagged as risky.

Governance Flag:
{application.governance_flag}

Confidence Score:
{application.confidence_score}

Final Matching Score:
{application.final_score}

This application requires manual governance review
because the confidence score exceeded the review threshold.

"""

    db.close()

    return explanation