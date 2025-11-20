"""Generate conversational follow-up messages for the intake agent."""

from __future__ import annotations

import random
from typing import Iterable

from openai import OpenAI

from project_agents.config.settings import get_settings
from project_agents.models import IntakeInsights, SummaryPayload

_FALLBACK_ACKS = [
    "Great, I captured {captured}.",
    "Thanks! I now know {captured}.",
    "Appreciate the detail on {captured}.",
    "Nice—that gives me a good handle on {captured}.",
    "Love it. I've logged {captured}.",
]

_FALLBACK_PROMPTS_SINGLE = [
    "Could you help me with {missing}?",
    "Next, I'd love to understand {missing}.",
    "When you have a moment, tell me about {missing}.",
    "To keep shaping the brief, could you walk me through {missing}?",
    "What can you share about {missing}?",
]

_FALLBACK_PROMPTS_MULTIPLE = [
    "Could you help me with {missing}?",
    "I'd love to understand {missing}.",
    "When you have a moment, tell me about {missing}.",
    "To keep shaping the brief, could you walk me through {missing}?",
]


def _format_fields(fields: Iterable[str]) -> str:
    items = list(dict.fromkeys(f.strip() for f in fields if f))
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" and {items[-1]}"


def _fallback_message(
    insights: IntakeInsights,
    follow_ups: list[str],
) -> str:
    """Generate fallback message for 1-2 questions."""
    captured = _format_fields(insights.captured_fields)
    num_questions = len(follow_ups)

    parts: list[str] = []
    if captured:
        template = random.choice(_FALLBACK_ACKS)
        parts.append(template.format(captured=captured))
    
    if num_questions == 0:
        parts.append("You're all set for now—feel free to keep refining the brief or ask for adjustments.")
    elif num_questions == 1:
        # Single question - ask naturally
        question = follow_ups[0]
        template = random.choice(_FALLBACK_PROMPTS_SINGLE)
        parts.append(template.format(missing=question.lower().rstrip("?")))
    else:
        # Two questions - combine naturally
        q1, q2 = follow_ups[0], follow_ups[1]
        # Remove question words to make it more natural
        q1_clean = q1.replace("What is ", "").replace("What ", "").replace("How ", "").replace("Who ", "").replace("Are ", "").rstrip("?")
        q2_clean = q2.replace("What is ", "").replace("What ", "").replace("How ", "").replace("Who ", "").replace("Are ", "").rstrip("?")
        parts.append(f"Could you help me with {q1_clean.lower()} and {q2_clean.lower()}?")

    return " ".join(parts)


def generate_follow_up_message(
    summary: SummaryPayload,
    follow_ups: list[str],
    insights: IntakeInsights,
) -> str:
    """Craft a conversational assistant reply for 1-2 questions.
    
    Args:
        summary: Current project summary
        follow_ups: List of 1-2 questions to ask
        insights: Captured and missing field insights
    
    Returns:
        Natural conversational message asking 1-2 questions
    """
    settings = get_settings()
    if settings.openai_api_key:
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            prompt = _build_prompt(summary, follow_ups, insights)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an empathetic project intake assistant. "
                            "Be friendly, natural, and conversational. "
                            "Ask only 1-2 questions at a time (not all at once). "
                            "CRITICAL: Only acknowledge information that is explicitly listed in the user's prompt. "
                            "Do not mention or infer any information that is not explicitly stated."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,  # Reduced for shorter, focused messages
                temperature=0.4,
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception:  # noqa: BLE001
            pass

    return _fallback_message(insights, follow_ups)


def _build_prompt(summary: SummaryPayload, follow_ups: list[str], insights: IntakeInsights) -> str:
    """Build prompt for LLM to generate conversational message with 1-2 questions."""
    captured = _format_fields(insights.captured_fields) or "nothing yet"
    num_questions = len(follow_ups)
    
    if num_questions == 0:
        questions_text = "No questions needed - all information captured."
    elif num_questions == 1:
        questions_text = f"Ask this ONE question naturally: {follow_ups[0]}"
    else:
        questions_text = f"Ask these TWO questions naturally (combine them in one sentence if possible):\n- {follow_ups[0]}\n- {follow_ups[1]}"
    
    # Build acknowledgment instruction
    if captured == "nothing yet":
        ack_instruction = "Do NOT acknowledge any captured information - nothing was captured in this turn."
    else:
        ack_instruction = f"ONLY acknowledge these specific items (and nothing else): {captured}."
    
    return (
        "You are an empathetic project intake assistant. "
        "Generate a brief, friendly message that:\n"
        f"1. {ack_instruction}\n"
        "2. Asks the question(s) naturally in a conversational way\n"
        "Keep it short (2-3 sentences max). Don't list all questions separately - combine them naturally.\n"
        "IMPORTANT: Only mention information that is explicitly listed above. Do not infer or mention anything else.\n"
        "\n"
        f"{questions_text}\n"
        "\n"
        "Generate a natural, conversational response:"
    )
