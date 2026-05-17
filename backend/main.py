import time

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
import backend.tools.policy_tool
import backend.tools.feedback_tool
import backend.tools.audit_tool
import backend.tools.hiring_data_tools
import backend.tools.outreach_tools

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

    last_error = None

    migration_statements = [
        """
        ALTER TABLE applications
        ALTER COLUMN governance_flag
        TYPE TEXT
        USING governance_flag::text
        """,
        """
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS application_id INTEGER
        """,
        """
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS action_type TEXT
        """,
        """
        ALTER TABLE audit_logs
        ADD COLUMN IF NOT EXISTS action_details TEXT
        """,
        """
        UPDATE audit_logs
        SET action_type = COALESCE(action_type, event_type)
        WHERE action_type IS NULL
        """,
        """
        UPDATE audit_logs
        SET action_details = COALESCE(action_details, event_details)
        WHERE action_details IS NULL
        """,
        """
        ALTER TABLE feedback
        ADD COLUMN IF NOT EXISTS session_id TEXT
        """,
        """
        CREATE TABLE IF NOT EXISTS email_drafts (
            id SERIAL PRIMARY KEY,
            candidate_id INTEGER REFERENCES candidates(id),
            job_id INTEGER REFERENCES jobs(id),
            subject TEXT,
            body TEXT,
            status TEXT DEFAULT 'DRAFT',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        ALTER TABLE feedback
        ADD COLUMN IF NOT EXISTS ai_response TEXT
        """,
        """
        UPDATE feedback
        SET ai_response = COALESCE(ai_response, response)
        WHERE ai_response IS NULL
        """,
        """
        ALTER TABLE conversation_memory
        ADD COLUMN IF NOT EXISTS message TEXT
        """,
        """
        UPDATE conversation_memory
        SET message = COALESCE(message, content)
        WHERE message IS NULL
        """,
        """
        ALTER TABLE conversation_memory
        ADD COLUMN IF NOT EXISTS memory_scope TEXT
        """
    ]

    for _ in range(10):

        try:

            with engine.begin() as conn:

                conn.execute(
                    text(schema)
                )

                for statement in migration_statements:

                    try:

                        conn.execute(
                            text(statement)
                        )

                    except Exception:

                        continue

            return

        except Exception as exc:

            last_error = exc
            time.sleep(3)

    raise last_error


initialize_database()


@app.get("/")
async def root():

    return {
        "message": "HireGuard AI running"
    }
