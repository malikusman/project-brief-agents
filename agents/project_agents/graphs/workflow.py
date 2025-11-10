"""Graph compilation helpers."""

from langgraph.graph import END, START, StateGraph

from project_agents.graphs.checkpointing import get_checkpointer
from project_agents.graphs.nodes import build_brief_node, build_intake_node
from project_agents.graphs.state import ProjectState


def build_project_brief_graph() -> StateGraph[ProjectState]:
    """Compile the project brief workflow graph."""

    graph_builder: StateGraph[ProjectState] = StateGraph(ProjectState)

    graph_builder.add_node("intake_agent", build_intake_node())
    graph_builder.add_node("brief_agent", build_brief_node())

    graph_builder.add_edge(START, "intake_agent")
    graph_builder.add_edge("intake_agent", "brief_agent")
    graph_builder.add_edge("brief_agent", END)

    checkpointer = get_checkpointer()
    return graph_builder.compile(checkpointer=checkpointer)


