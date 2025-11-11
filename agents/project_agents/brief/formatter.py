"""Shape intake summaries into Lovable-style brief sections."""

from __future__ import annotations

from typing import Any, Dict, List


def build_brief(summary: dict[str, Any]) -> Dict[str, Any]:
    """Convert an intake summary into the Lovable brief layout."""

    description = _coalesce(
        [
            summary.get("problem"),
            summary.get("solution"),
        ],
        default="This brief will be expanded as the intake conversation gathers more context.",
    )

    purpose = summary.get(
        "solution",
        "Clarify the project's purpose once additional details are collected.",
    )

    outcomes = _split_points(
        summary.get("success_metrics"),
        fallback=[
            "Define success metrics that indicate adoption and impact.",
            "Identify measurable outcomes aligned with strategic goals.",
        ],
    )

    business_model = _split_points(
        summary.get("resources"),
        fallback=[
            "List revenue streams, partnerships, or resource requirements.",
            "Outline go-to-market considerations and support needs.",
        ],
    )

    constraints = summary.get("constraints") or "Surface constraints, risks, and dependencies during intake."
    timeline = summary.get("timeline") or "Map the project timeline with key milestones during intake."

    return {
        "project_description": description,
        "purpose": purpose,
        "expected_outcomes": outcomes,
        "business_model": business_model,
        "constraints": constraints,
        "timeline": timeline,
        "target_users": summary.get("target_users"),
        "documents": summary.get("documents", []),
    }


def _coalesce(candidates: List[str | None], default: str) -> str:
    for candidate in candidates:
        if candidate and candidate.strip():
            return candidate.strip()
    return default


def _split_points(text: str | None, fallback: List[str]) -> List[str]:
    if not text or not text.strip():
        return fallback
    items = [item.strip(" -•") for item in text.replace("\n", ";").split(";")]
    return [item for item in items if item]

