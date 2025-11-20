"""Question priority queue for conversational intake flow."""

from __future__ import annotations

from typing import TypedDict

from project_agents.models import SummaryPayload


class QuestionItem(TypedDict, total=False):
    """Represents a single question in the priority queue."""

    field: str  # Field name (e.g., "project_title")
    question: str  # The question text
    priority: int  # Lower number = higher priority (1 is highest)
    asked: bool  # Whether this question has been asked before
    asked_at: str | None  # Timestamp when asked (optional)


# Priority order: lower number = higher priority
FIELD_PRIORITIES = {
    "project_title": 1,  # Highest priority
    "problem": 2,
    "solution": 3,
    "target_users": 4,
    "success_metrics": 5,
    "timeline": 6,
    "constraints": 7,
    "resources": 8,  # Lowest priority
}

# Question text for each field
FIELD_QUESTIONS = {
    "project_title": "What is the working title or name of the project?",
    "problem": "What problem or opportunity are you addressing?",
    "solution": "How will you solve the problem or deliver value?",
    "target_users": "Who are the primary users or stakeholders?",
    "success_metrics": "How will you measure success?",
    "constraints": "Are there any constraints, risks, or dependencies?",
    "timeline": "What is the timeline or key milestones?",
    "resources": "What resources, documents, or tools do you have?",
}


def build_question_queue(summary: SummaryPayload) -> list[QuestionItem]:
    """Build a prioritized queue of questions for missing fields.
    
    Args:
        summary: The current summary with captured fields
    
    Returns:
        List of QuestionItem objects sorted by priority (highest first)
    """
    queue: list[QuestionItem] = []
    
    for field, priority in sorted(FIELD_PRIORITIES.items(), key=lambda x: x[1]):
        # Check if field is missing or empty
        value = getattr(summary, field, None)
        is_missing = (
            value is None
            or (isinstance(value, str) and not value.strip())
            or (isinstance(value, list) and len(value) == 0)
        )
        
        if is_missing:
            queue.append(
                QuestionItem(
                    field=field,
                    question=FIELD_QUESTIONS[field],
                    priority=priority,
                    asked=False,
                    asked_at=None,
                )
            )
    
    return queue


def get_next_questions(
    queue: list[QuestionItem],
    max_questions: int = 2,
) -> list[QuestionItem]:
    """Get the next 1-2 questions from the queue (highest priority, not asked yet).
    
    Args:
        queue: The question queue
        max_questions: Maximum number of questions to return (default: 2)
    
    Returns:
        List of 1-2 QuestionItem objects (highest priority, unanswered)
    """
    # Filter to unanswered questions, sorted by priority
    unanswered = [q for q in queue if not q.get("asked", False)]
    unanswered.sort(key=lambda x: x.get("priority", 999))
    
    # Return up to max_questions
    return unanswered[:max_questions]


def mark_questions_asked(
    queue: list[QuestionItem],
    fields: list[str],
) -> list[QuestionItem]:
    """Mark questions as asked for the given fields.
    
    Args:
        queue: The question queue
        fields: List of field names to mark as asked
    
    Returns:
        Updated queue with asked flags set
    """
    field_set = set(fields)
    updated_queue = []
    
    for item in queue:
        if item["field"] in field_set:
            updated_item = QuestionItem(**item)
            updated_item["asked"] = True
            updated_queue.append(updated_item)
        else:
            updated_queue.append(item)
    
    return updated_queue


def update_queue_from_summary(
    old_summary: SummaryPayload | None,
    new_summary: SummaryPayload,
    existing_queue: list[QuestionItem],
) -> list[QuestionItem]:
    """Update question queue based on newly captured fields.
    
    Args:
        old_summary: Previous summary (None if first time)
        new_summary: Current summary after analysis
        existing_queue: Existing question queue
    
    Returns:
        Updated queue with newly answered questions removed
    """
    # Build fresh queue from new summary
    new_queue = build_question_queue(new_summary)
    
    # Preserve "asked" status from existing queue
    asked_fields = {
        item["field"]: item.get("asked", False)
        for item in existing_queue
        if item.get("asked", False)
    }
    
    # Mark questions as asked if they were asked before
    for item in new_queue:
        if item["field"] in asked_fields:
            item["asked"] = True
    
    return new_queue

