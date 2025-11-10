"""State definitions for LangGraph workflow."""

from typing import Any, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage


class ProjectState(TypedDict, total=False):
    """Composite state maintained across the workflow."""

    messages: list[BaseMessage]
    summary: dict[str, Any]
    brief: dict[str, Any]


def initialize_state(user_input: str) -> ProjectState:
    """Helper to bootstrap graph execution with a default message list."""

    return {
        "messages": [HumanMessage(content=user_input)],
    }


