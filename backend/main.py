from fastapi import FastAPI

from sqlalchemy import text

from database.connection import (
    engine
)

from backend.admin_routes import (
    router as admin_router
)
import backend.tools.recruiter_tools
import backend.tools.governance_tools
import backend.tools.operations_tools
import backend.tools.email_tools
import backend.tools.governance_explainer_tool
import backend.tools.governance_analytics_tool
import backend.tools.recruitment_analytics_tool
import backend.tools.policy_tools


app = FastAPI(
    title="HireGuard AI"
)

app.include_router(admin_router)


def initialize_database():

    with open(
        "database/schema.sql",
        "r"
    ) as f:

        schema = f.read()

    with engine.connect() as conn:

        conn.execute(
            text(schema)
        )

        conn.commit()


initialize_database()


@app.get("/")
async def root():

    return {
        "message": "HireGuard AI running"
    }
