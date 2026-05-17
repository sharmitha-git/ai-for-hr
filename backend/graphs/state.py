from typing import TypedDict
from typing import Any


class HiringState(TypedDict, total=False):

    query: str

    selected_agent: str

    governance_summary: Any

    governance_results: Any

    workflow: Any

    audit_logs: Any

    candidates: Any

    message: str

    response: str

    memory: list
    session_id: str
    trace_id: str
