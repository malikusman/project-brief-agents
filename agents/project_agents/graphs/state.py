"""State definitions for LangGraph workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from project_agents.intake.question_queue import QuestionItem


class ConversationTurn(TypedDict):
    """Serialized representation of a conversation message."""

    role: str
    content: str


class DocumentReference(TypedDict, total=False):
    """Metadata representing an uploaded document."""

    id: str
    name: str
    url: str | None
    notes: str | None
    text: str | None


class ProjectState(TypedDict, total=False):
    """Composite state maintained across the workflow."""

    messages: list[BaseMessage]
    conversation: list[ConversationTurn]
    documents: list[DocumentReference]
    summary: dict[str, Any]
    brief: dict[str, Any]
    question_queue: list[QuestionItem]  # Prioritized queue of questions
    current_questions: list[QuestionItem]  # 1-2 questions currently being asked
    follow_up_questions: list[str]  # Backward compatibility (kept for now)
    assistant_message: str


def initialize_state(
    conversation: list[ConversationTurn],
    documents: list[DocumentReference],
) -> ProjectState:
    """Bootstrap graph execution with conversation history and documents."""

    messages = [_to_message(turn) for turn in conversation]
    return {
        "messages": messages,
        "conversation": conversation,
        "documents": documents,
    }


def _to_message(turn: ConversationTurn) -> BaseMessage:
    role = turn.get("role", "user").lower()
    content = turn.get("content", "")
    if role == "assistant":
        return AIMessage(content=content)
    if role == "system":
        return SystemMessage(content=content)
    return HumanMessage(content=content)


def to_message(turn: ConversationTurn) -> BaseMessage:
    """Convert a ConversationTurn to a LangChain BaseMessage. Public API."""
    return _to_message(turn)

