from backend.tools.tool_registry import (
    register_tool
)


from database.connection import SessionLocal 

from backend.entities import Application


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