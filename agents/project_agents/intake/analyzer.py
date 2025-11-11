"""Lightweight heuristics to extract structured context and follow-up questions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


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


@dataclass
class IntakeSummary:
    project_title: str | None = None
    problem: str | None = None
    solution: str | None = None
    target_users: str | None = None
    success_metrics: str | None = None
    constraints: str | None = None
    timeline: str | None = None
    resources: str | None = None
    documents: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "project_title": self.project_title,
            "problem": self.problem,
            "solution": self.solution,
            "target_users": self.target_users,
            "success_metrics": self.success_metrics,
            "constraints": self.constraints,
            "timeline": self.timeline,
            "resources": self.resources,
            "documents": self.documents,
        }


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


def analyze_prompt(prompt: str, documents: list[str] | None = None) -> Tuple[dict, list[str]]:
    """Parse the prompt into a structured summary and collect follow-up questions."""

    documents = documents or []
    sentences = _sentences(prompt)
    summary = IntakeSummary(project_title=_extract_title(prompt), documents=documents)

    for key, keywords in KEYWORD_MAP.items():
        value = _first_sentence_with_keyword(sentences, keywords)
        if value:
            setattr(summary, key, value)

    if documents:
        summary.resources = summary.resources or ", ".join(documents)
        summary.documents.extend(documents)

    missing = [
        SUMMARY_FIELDS[field] for field, value in summary.to_dict().items()
        if field in SUMMARY_FIELDS and (value is None or not value.strip())
    ]

    return summary.to_dict(), missing


def _first_sentence_with_keyword(sentences: list[str], keywords: list[str]) -> str | None:
    for sentence in sentences:
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            return sentence.strip()
    return None

