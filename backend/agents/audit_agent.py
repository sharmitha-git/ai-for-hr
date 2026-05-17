def audit_agent(state):

    audit_message = f"""

Audit completed successfully.

Selected Agent:
{state.get('selected_agent')}

User Query:
{state.get('query')}

"""

    state["audit_logs"] = (
        audit_message
    )

    return state