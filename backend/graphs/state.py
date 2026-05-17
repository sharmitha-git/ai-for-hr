from typing import Any
from typing import TypedDict


class HiringState(TypedDict, total=False):

    query: str
    session_id: str
    trace_id: str
    job_id: int

    selected_agent: str
    selected_tool: str
    route_type: str
    retrieval_domain: str

    tool_args: dict[str, Any]
    agent_sequence: list[str]
    current_step: int
    next_agent: str

    orchestration_log: list[str]
    agent_outputs: dict[str, Any]

    governance_summary: Any
    governance_results: Any
    workflow: Any
    audit_logs: Any
    candidates: Any
    message: str
    response: str
    memory: str
    memory_scope: str
    error: str
    email_draft: Any
