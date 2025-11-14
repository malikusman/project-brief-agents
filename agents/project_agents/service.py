"""High-level interface for running the LangGraph workflow."""

from typing import Iterable, Mapping

from project_agents.graphs.state import (
    ConversationTurn,
    DocumentReference,
    ProjectState,
    initialize_state,
)
from project_agents.graphs.workflow import build_project_brief_graph
from project_agents.models import BriefPayload, LovableBrief, SummaryPayload


def run_project_brief_workflow(
    conversation: Iterable[Mapping[str, str]],
    documents: Iterable[Mapping[str, str | None]] | None = None,
    thread_id: str | None = None,
) -> dict:
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
                    text=doc.get("text"),
                )
            )

    graph = build_project_brief_graph()
    initial_state = initialize_state(conversation_list, document_list)
    thread_identifier = thread_id or generate_thread_id()
    config = {"configurable": {"thread_id": thread_identifier}}
    result = graph.invoke(initial_state, config=config)

    summary_payload = SummaryPayload(**result.get("summary", {}))
    brief_payload = LovableBrief(**result.get("brief", {}))
    follow_ups = result.get("follow_up_questions", [])
    assistant_message = result.get("assistant_message") or ""

    agent_payload = BriefPayload(
        summary=summary_payload,
        brief=brief_payload,
        follow_up_questions=follow_ups,
        thread_id=thread_identifier,
        assistant_message=assistant_message,
    )
    return agent_payload.model_dump()


def generate_thread_id() -> str:
    """Generate a deterministic thread id."""

    from uuid import uuid4

    return f"thread-{uuid4()}"
