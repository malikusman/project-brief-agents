"""High-level interface for running the LangGraph workflow."""

from typing import cast

from project_agents.graphs.state import ProjectState, initialize_state
from project_agents.graphs.workflow import build_project_brief_graph


def run_project_brief_workflow(user_input: str) -> ProjectState:
    """Execute the workflow using the provided user input."""

    graph = build_project_brief_graph()
    initial_state = initialize_state(user_input)
    config = {"configurable": {"thread_id": generate_thread_id()}}
    result = graph.invoke(initial_state, config=config)
    return cast(ProjectState, result)


def generate_thread_id() -> str:
    """Generate a deterministic thread id."""

    from uuid import uuid4

    return f"thread-{uuid4()}"

