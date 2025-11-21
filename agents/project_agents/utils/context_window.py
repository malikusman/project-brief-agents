"""Simple context window - keeps last N messages only."""

from __future__ import annotations

from project_agents.config.settings import get_settings
from project_agents.graphs.state import ConversationTurn


def get_recent_messages(
    conversation: list[ConversationTurn],
    max_messages: int | None = None,
) -> str:
    """Get recent messages from conversation, keeping only last N messages.
    
    Includes both user and assistant messages to maintain conversation context.
    
    Args:
        conversation: List of conversation turns (user and assistant messages)
        max_messages: Maximum number of messages to include (default: from settings, default: 15)
    
    Returns:
        Formatted conversation text with alternating user/assistant messages from last N messages
    """
    if not conversation:
        return ""
    
    # Get max_messages from settings if not provided
    if max_messages is None:
        settings = get_settings()
        max_messages = settings.conversation_window_size
    
    # Keep last N messages total (both user and assistant)
    recent_turns = conversation[-max_messages:] if len(conversation) > max_messages else conversation
    
    # Format as alternating user/assistant messages
    formatted_messages = []
    for turn in recent_turns:
        role = turn.get("role", "user").lower()
        content = turn.get("content", "").strip()
        if not content:
            continue
        
        if role == "assistant":
            formatted_messages.append(f"Assistant: {content}")
        elif role == "user":
            formatted_messages.append(f"User: {content}")
        else:
            # Handle system or other roles
            formatted_messages.append(f"{role.capitalize()}: {content}")
    
    # Combine messages with newlines
    return "\n".join(formatted_messages)

