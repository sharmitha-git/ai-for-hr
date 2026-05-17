from pydantic import BaseModel


class CopilotRequest(BaseModel):

    query: str


class ApplicationStatusUpdate(BaseModel):

    application_id: int

    application_status: str

    reviewer_name: str | None = "human_reviewer"

    reviewer_notes: str | None = None
