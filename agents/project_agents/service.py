"""High-level interface for running the LangGraph workflow."""

from typing import Iterable, Mapping, cast

from project_agents.graphs.state import (
    ConversationTurn,
    DocumentReference,
    ProjectState,
    initialize_state,
)
from project_agents.graphs.workflow import build_project_brief_graph
from project_agents.models import AgentRunModel, BriefModel, SummaryModel


def run_project_brief_workflow(
    conversation: Iterable[Mapping[str, str]],
    documents: Iterable[Mapping[str, str | None]] | None = None,
    thread_id: str | None = None,
) -> ProjectState:
    """Execute the workflow using the provided user input."""

    conversation_list = [
        ConversationTurn(role=turn.get("role", "user"), content=turn.get("content", ""))
        for turn in conversation
    ]
    if not conversation_list:
        raise ValueError("conversation must contain at least one message.")

    document_list: list[DocumentReference] = []
    if documents:
        for doc in documents:
            document_list.append(
                DocumentReference(
                    id=str(doc.get("id", "")),
                    name=str(doc.get("name", "")),
                    url=doc.get("url"),
                    notes=doc.get("notes"),
                )
            )

    graph = build_project_brief_graph()
    initial_state = initialize_state(conversation_list, document_list)
    thread_identifier = thread_id or generate_thread_id()
    config = {"configurable": {"thread_id": thread_identifier}}
    result = graph.invoke(initial_state, config=config)
    project_state = cast(ProjectState, result)
    project_state["thread_id"] = thread_identifier
    project_state.setdefault("follow_up_questions", [])

    summary_model = SummaryModel(**project_state.get("summary", {}))
    brief_model = BriefModel(**project_state.get("brief", {}))
    agent_model = AgentRunModel(
        summary=summary_model,
        brief=brief_model,
        follow_up_questions=project_state.get("follow_up_questions", []),
        thread_id=thread_identifier,
    )
    return cast(ProjectState, agent_model.model_dump())


def generate_thread_id() -> str:
    """Generate a deterministic thread id."""

    from uuid import uuid4

    return f"thread-{uuid4()}"
