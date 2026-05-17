from backend.tools.tool_registry import (
    register_tool
)

from database.connection import (
    SessionLocal
)

from backend.entities import (
    Application
)


@register_tool(
    "governance_statistics"
)
def governance_statistics():

    db = SessionLocal()

    applications = db.query(
        Application
    ).all()

    total = len(applications)

    risky = [

        a for a in applications

        if a.governance_flag == "REVIEW"
    ]

    approved = [

        a for a in applications

        if a.governance_flag == "APPROVED"
    ]

    rejected = [

        a for a in applications

        if a.governance_flag == "REJECTED"
    ]

    avg_score = 0

    if applications:

        avg_score = sum(

            a.final_score
            for a in applications

        ) / total

    db.close()

    return {

        "total_applications":
            total,

        "risky_count":
            len(risky),

        "approved_count":
            len(approved),

        "rejected_count":
            len(rejected),

        "average_score":
            round(avg_score, 2)
    }