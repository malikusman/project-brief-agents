"""Simple context window - keeps last N messages only."""

from __future__ import annotations

from project_agents.config.settings import get_settings
from project_agents.graphs.state import ConversationTurn


def get_recent_messages(
    conversation: list[ConversationTurn],
    max_messages: int | None = None,
) -> str:
    """Get recent messages from conversation, keeping only last N messages.
    
    Args:
        conversation: List of conversation turns
        max_messages: Maximum number of messages to include (default: from settings, default: 15)
    
    Returns:
        Concatenated conversation text from last N messages
    """
    if not conversation:
        return ""
    
    # Get max_messages from settings if not provided
    if max_messages is None:
        settings = get_settings()
        max_messages = settings.conversation_window_size
    
    # Take only user messages
    user_messages = [
        turn["content"]
        for turn in conversation
        if turn.get("role", "user").lower() == "user"
    ]
    
    # Limit to last N messages
    if len(user_messages) > max_messages:
        user_messages = user_messages[-max_messages:]
    
    # Combine messages
    return "\n".join(msg for msg in user_messages if msg)

