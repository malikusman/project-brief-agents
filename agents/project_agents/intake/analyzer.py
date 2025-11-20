"""Lightweight heuristics to extract structured context and follow-up questions."""

from __future__ import annotations

import json
from typing import List, Tuple

from openai import OpenAI

from project_agents.config.settings import get_settings
from project_agents.models import IntakeInsights, SummaryPayload
from project_agents.intake.question_queue import QuestionItem, build_question_queue


SUMMARY_FIELDS = {
    "project_title": "What is the working title or name of the project?",
    "problem": "What problem or opportunity are you addressing?",
    "solution": "How will you solve the problem or deliver value?",
    "target_users": "Who are the primary users or stakeholders?",
    "success_metrics": "How will you measure success?",
    "constraints": "Are there any constraints, risks, or dependencies?",
    "timeline": "What is the timeline or key milestones?",
    "resources": "What resources, documents, or tools do you have?",
}

KEYWORD_MAP = {
    "problem": ["problem", "challenge", "pain", "issue", "need"],
    "solution": ["solution", "approach", "strategy", "idea"],
    "target_users": ["user", "audience", "customer", "stakeholder"],
    "success_metrics": ["success", "metric", "kpi", "measure"],
    "constraints": ["constraint", "risk", "concern", "dependency", "limitation"],
    "timeline": ["timeline", "deadline", "milestone", "schedule"],
    "resources": ["resource", "document", "tool", "asset", "reference"],
}


def _extract_with_llm(
    prompt: str,
    documents: list[str] | None = None,
) -> SummaryPayload | None:
    """Extract structured information using OpenAI LLM. Returns None if extraction fails."""
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    documents = documents or []
    document_context = ""
    if documents:
        document_context = f"\n\nUploaded documents: {', '.join(documents)}"

    extraction_prompt = f"""You are a project intake assistant. Extract structured information from the following project description. The description may be in any language - extract information regardless of the language used.

Project description:
{prompt}{document_context}

Extract the following information and return it as a JSON object:
- project_title: The name or title of the project (string, default to "Untitled Project" if not found)
- problem: What problem or opportunity is being addressed (string or null)
- solution: How the problem will be solved or value delivered (string or null)
- target_users: Who are the primary users or stakeholders (array of strings, empty if not found)
- success_metrics: How success will be measured (array of strings, empty if not found)
- constraints: Any constraints, risks, or dependencies (array of strings, empty if not found)
- timeline: Timeline or key milestones (string or null)
- resources: Resources, documents, or tools mentioned (array of strings, empty if not found)
- documents: List of document names provided (array of strings, use the provided list)
- opportunity_areas: Derived opportunities based on the project (array of strings, empty if not found)

Return ONLY valid JSON, no additional text. Example format:
{{
  "project_title": "Example Project",
  "problem": "Users struggle with X",
  "solution": "We will build Y",
  "target_users": ["students", "teachers"],
  "success_metrics": ["25% increase in engagement"],
  "constraints": ["Budget cap $200k"],
  "timeline": "6 months",
  "resources": ["Existing API", "Design system"],
  "documents": {json.dumps(documents)},
  "opportunity_areas": ["Deliver the solution: Y"]
}}"""

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured information from project descriptions. Always respond with valid JSON only.",
                },
                {"role": "user", "content": extraction_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        if not content:
            return None

        # Parse JSON response
        data = json.loads(content)

        # Build SummaryPayload from extracted data
        summary = SummaryPayload(
            project_title=data.get("project_title", "Untitled Project"),
            problem=data.get("problem"),
            solution=data.get("solution"),
            target_users=data.get("target_users", []),
            success_metrics=data.get("success_metrics", []),
            constraints=data.get("constraints", []),
            timeline=data.get("timeline"),
            resources=data.get("resources", []),
            documents=data.get("documents", documents),
            opportunity_areas=data.get("opportunity_areas", []),
        )

        # Derive opportunity areas if not provided
        if not summary.opportunity_areas:
            summary.opportunity_areas = _derive_opportunities(summary)

        return summary

    except Exception:  # noqa: BLE001
        # Return None on any error to trigger fallback
        return None


def _extract_with_keywords(
    prompt: str,
    documents: list[str] | None = None,
) -> SummaryPayload:
    """Extract structured information using keyword-based heuristics (fallback method)."""
    documents = documents or []
    sentences = _sentences(prompt)

    raw: dict[str, str | list[str] | None] = {
        "project_title": _extract_title(prompt),
        "documents": list(documents),
    }

    for key, keywords in KEYWORD_MAP.items():
        value = _first_sentence_with_keyword(sentences, keywords)
        if value:
            raw[key] = value

    if documents and not raw.get("resources"):
        raw["resources"] = ", ".join(documents)

    summary = SummaryPayload(
        project_title=raw.get("project_title") or "Untitled Project",
        problem=_to_optional_str(raw.get("problem")),
        solution=_to_optional_str(raw.get("solution")),
        target_users=_normalize_list(raw.get("target_users")),
        success_metrics=_normalize_list(raw.get("success_metrics")),
        constraints=_normalize_list(raw.get("constraints")),
        timeline=_to_optional_str(raw.get("timeline")),
        resources=_normalize_list(raw.get("resources")),
        documents=list(documents),
    )

    if not summary.opportunity_areas:
        summary.opportunity_areas = _derive_opportunities(summary)

    return summary


def analyze_prompt(
    prompt: str,
    documents: list[str] | None = None,
) -> Tuple[SummaryPayload, list[QuestionItem], IntakeInsights]:
    """Parse the prompt into a structured summary and collect follow-up questions.
    
    Tries LLM-based extraction first, falls back to keyword-based extraction if LLM fails.
    Returns a prioritized question queue instead of a flat list.
    """
    documents = documents or []

    # Try LLM extraction first
    summary = _extract_with_llm(prompt, documents)

    # Fallback to keyword-based extraction if LLM fails
    if summary is None:
        summary = _extract_with_keywords(prompt, documents)

    # Build prioritized question queue
    question_queue = build_question_queue(summary)

    # Generate insights (for backward compatibility and tone generation)
    captured_fields: list[str] = []
    missing_fields: list[str] = []

    for field, question in SUMMARY_FIELDS.items():
        value = getattr(summary, field)
        # Check if field is actually captured (not default/empty)
        is_captured = False
        if field == "project_title":
            # project_title has default "Untitled Project" - only count as captured if user provided a real title
            is_captured = value and value != "Untitled Project" and value.strip()
        elif isinstance(value, list):
            is_captured = len(value) > 0
        elif isinstance(value, str):
            is_captured = bool(value and value.strip())
        else:
            is_captured = value is not None
        
        if is_captured:
            captured_fields.append(field.replace("_", " "))
        else:
            missing_fields.append(question.replace("What ", "").replace("How ", "").replace("Are ", "").rstrip("?"))

    insights = IntakeInsights(
        captured_fields=captured_fields,
        missing_fields=missing_fields,
    )

    # For backward compatibility, also return list of question strings
    # (nodes.py will be updated to use the queue directly)
    follow_up_questions = [item["question"] for item in question_queue]

    return summary, question_queue, insights


def _sentences(text: str) -> list[str]:
    raw = [segment.strip() for segment in text.replace("\n", ". ").split(".")]
    return [segment for segment in raw if segment]


def _extract_title(prompt: str) -> str | None:
    lowered = prompt.lower()
    markers = ["project called", "project name is", "initiative", "product"]
    for marker in markers:
        if marker in lowered:
            idx = lowered.index(marker)
            snippet = prompt[idx:].split("\n", 1)[0]
            return snippet.split(" ", len(marker.split()) + 5)[-1].strip().strip(":")
    first_sentence = _sentences(prompt)
    if first_sentence:
        fragment = first_sentence[0]
        if len(fragment.split()) > 3:
            return fragment[:120].strip()
    return None


def _first_sentence_with_keyword(sentences: list[str], keywords: list[str]) -> str | None:
    for sentence in sentences:
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            return sentence.strip()
    return None


def _normalize_list(value: str | list[str] | None) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [item.strip() for item in value if item]
    return [item for item in _split_str(value)]


def _split_str(value: str) -> list[str]:
    separators = [";", ",", "\n", " and "]
    items = [value]
    for sep in separators:
        new_items: list[str] = []
        for item in items:
            new_items.extend(item.split(sep))
        items = new_items
    return [item.strip(" -•").strip() for item in items if item.strip()]


def _derive_opportunities(summary: SummaryPayload) -> list[str]:
    hints: list[str] = []
    if summary.solution:
        hints.append(f"Deliver the solution: {summary.solution}")
    if summary.problem:
        hints.append(f"Address the problem: {summary.problem}")
    if summary.target_users:
        hints.append(f"Delight {', '.join(summary.target_users)}")
    return hints


def _to_optional_str(value: str | list[str] | None) -> str | None:
    if isinstance(value, list):
        joined = ", ".join(str(item) for item in value if item)
        return joined or None
    if isinstance(value, str):
        return value.strip() or None
    return None
