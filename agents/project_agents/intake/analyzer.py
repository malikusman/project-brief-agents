"""Lightweight heuristics to extract structured context and follow-up questions."""

from __future__ import annotations

from typing import List, Tuple

from project_agents.models import SummaryPayload


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


def analyze_prompt(
    prompt: str,
    documents: list[str] | None = None,
) -> Tuple[SummaryPayload, list[str]]:
    """Parse the prompt into a structured summary and collect follow-up questions."""

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

    missing = [
        SUMMARY_FIELDS[field]
        for field in SUMMARY_FIELDS
        if not getattr(summary, field)
    ]

    return summary, missing


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
