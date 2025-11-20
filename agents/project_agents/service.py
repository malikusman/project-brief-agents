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


def _extract_new_messages(
    incoming_conversation: list[ConversationTurn],
    existing_conversation: list[ConversationTurn],
) -> list[ConversationTurn]:
    """Extract only new messages that don't exist in the previous conversation."""
    if not existing_conversation:
        return incoming_conversation

    # Create a set of existing message signatures (role + content)
    existing_signatures = {
        (turn.get("role", ""), turn.get("content", "")) for turn in existing_conversation
    }

    # Filter out messages that already exist
    new_messages = [
        turn
        for turn in incoming_conversation
        if (turn.get("role", ""), turn.get("content", "")) not in existing_signatures
    ]

    return new_messages


def _merge_documents(
    incoming_documents: list[DocumentReference],
    existing_documents: list[DocumentReference],
) -> list[DocumentReference]:
    """Merge incoming documents with existing ones, avoiding duplicates by ID."""
    if not existing_documents:
        return incoming_documents

    existing_ids = {doc.get("id", "") for doc in existing_documents if doc.get("id")}
    new_documents = [
        doc for doc in incoming_documents if doc.get("id", "") not in existing_ids
    ]

    # Combine existing and new documents
    return list(existing_documents) + new_documents


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
    thread_identifier = thread_id or generate_thread_id()
    config = {"configurable": {"thread_id": thread_identifier}}

    # Try to load existing state from checkpoint if thread_id exists
    if thread_id:
        try:
            # Get current state from checkpoint
            current_state = graph.get_state(config)
            if current_state and current_state.values:
                existing_state = current_state.values
                existing_conversation = existing_state.get("conversation", [])
                existing_documents = existing_state.get("documents", [])

                # Extract only new messages and documents
                new_messages = _extract_new_messages(conversation_list, existing_conversation)
                merged_documents = _merge_documents(document_list, existing_documents)

                # If there are new messages or documents, merge them into existing state
                if new_messages or merged_documents != existing_documents:
                    # Merge new messages into existing conversation
                    merged_conversation = list(existing_conversation) + new_messages

                    # Create update state with only new data
                    from project_agents.graphs.state import to_message

                    new_messages_langchain = [to_message(turn) for turn in new_messages]
                    update_state: ProjectState = {
                        "conversation": merged_conversation,
                        "documents": merged_documents,
                        "messages": existing_state.get("messages", []) + new_messages_langchain,
                    }

                    # Update the state and run the graph
                    result = graph.invoke(update_state, config=config)
                else:
                    # No new messages, return existing state
                    result = existing_state
            else:
                # No checkpoint exists, create fresh state
                initial_state = initialize_state(conversation_list, document_list)
                result = graph.invoke(initial_state, config=config)
        except Exception:
            # If checkpoint retrieval fails, fall back to fresh state
            initial_state = initialize_state(conversation_list, document_list)
            result = graph.invoke(initial_state, config=config)
    else:
        # First time - create fresh state
        initial_state = initialize_state(conversation_list, document_list)
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
