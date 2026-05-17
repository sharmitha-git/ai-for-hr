from langgraph.graph import (
    StateGraph,
    END
)

from backend.graphs.state import (
    HiringState
)

from backend.agents.supervisor_agent import (
    supervisor_agent
)

from backend.agents.recruiter_agent import (
    recruiter_agent
)

from backend.agents.governance_agent import (
    governance_agent
)

from backend.agents.operations_agent import (
    operations_agent
)

workflow = StateGraph(
    HiringState
)

workflow.add_node(
    "supervisor",
    supervisor_agent
)

workflow.add_node(
    "recruiter",
    recruiter_agent
)

workflow.add_node(
    "governance",
    governance_agent
)

workflow.add_node(
    "operations",
    operations_agent
)

workflow.set_entry_point(
    "supervisor"
)

def route_agent(state):

    return state[
        "selected_agent"
    ]

workflow.add_conditional_edges(

    "supervisor",

    route_agent,

    {

        "recruiter":
            "recruiter",

        "governance":
            "governance",

        "operations":
            "operations"
    }
)

workflow.add_edge(
    "recruiter",
    END
)

workflow.add_edge(
    "governance",
    END
)

workflow.add_edge(
    "operations",
    END
)

hiring_graph = (
    workflow.compile()
)