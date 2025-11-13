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

_FALLBACK_PROMPTS = [
    "Could you help me with {missing}?",
    "Next, I'd love to understand {missing}.",
    "When you have a moment, tell me about {missing}.",
    "To keep shaping the brief, could you walk me through {missing}?",
    "What can you share about {missing}?",
]


def _format_fields(fields: Iterable[str]) -> str:
    items = list(dict.fromkeys(f.strip() for f in fields if f))
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" and {items[-1]}"


def _fallback_message(insights: IntakeInsights) -> str:
    captured = _format_fields(insights.captured_fields)
    missing = _format_fields(insights.missing_fields)

    parts: list[str] = []
    if captured:
        template = random.choice(_FALLBACK_ACKS)
        parts.append(template.format(captured=captured))
    if missing:
        template = random.choice(_FALLBACK_PROMPTS)
        parts.append(template.format(missing=missing))
    else:
        parts.append("You're all set for now—feel free to keep refining the brief or ask for adjustments.")

    return " ".join(parts)


def generate_follow_up_message(
    summary: SummaryPayload,
    follow_ups: list[str],
    insights: IntakeInsights,
) -> str:
    """Craft a conversational assistant reply."""

    settings = get_settings()
    if settings.openai_api_key:
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            prompt = _build_prompt(summary, follow_ups, insights)
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                max_output_tokens=256,
                temperature=0.4,
            )
            content = response.output_text.strip()
            if content:
                return content
        except Exception:  # noqa: BLE001
            pass

    return _fallback_message(insights)


def _build_prompt(summary: SummaryPayload, follow_ups: list[str], insights: IntakeInsights) -> str:
    captured = _format_fields(insights.captured_fields) or "nothing yet"
    missing = "\n".join(f"- {item}" for item in follow_ups) or "- None"
    return (
        "You are an empathetic project intake assistant."
        " Summarize what you just learned in a friendly tone and clearly list what you still need."
        " Avoid sounding robotic or repetitive. End with a natural question when more info is needed."
        "\n\n"
        f"Captured so far: {captured}."
        "\nKey project facts:"
        f"\n- Problem: {summary.problem or 'pending'}"
        f"\n- Solution: {summary.solution or 'pending'}"
        f"\n- Target users: {', '.join(summary.target_users) or 'pending'}"
        f"\n- Success metrics: {', '.join(summary.success_metrics) or 'pending'}"
        f"\n- Constraints: {', '.join(summary.constraints) or 'pending'}"
        f"\n- Timeline: {summary.timeline or 'pending'}"
        "\n\nOutstanding needs:\n"
        f"{missing}"
    )
