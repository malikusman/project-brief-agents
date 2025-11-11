"""Shape intake summaries into Lovable-style brief sections."""

from __future__ import annotations

from typing import List

from project_agents.models import BriefModel, SummaryModel


def build_brief(summary: SummaryModel) -> BriefModel:
    """Convert an intake summary into the Lovable brief layout."""

    description = _coalesce(
        [
            summary.problem,
            summary.solution,
        ],
        default="This brief will be expanded as the intake conversation gathers more context.",
    )

    purpose = summary.solution or "Clarify the project's purpose once additional details are collected."

    outcomes = summary.success_metrics or [
        "Define success metrics that indicate adoption and impact.",
        "Identify measurable outcomes aligned with strategic goals.",
    ]

    business_model = summary.resources or [
        "List revenue streams, partnerships, or resource requirements.",
        "Outline go-to-market considerations and support needs.",
    ]

    risks = summary.constraints or [
        "Surface constraints, risks, and dependencies during intake."
    ]

    timeline = summary.timeline or "Map the project timeline with key milestones during intake."

    opportunity = summary.opportunities or [
        "Explore adjacent opportunities uncovered during discovery.",
        "Validate market demand and differentiation opportunities.",
    ]

    suggested_reads = [
        "Add foundational research or industry reports to guide the team.",
    ]

    ideas_board = [
        "Capture brainstorm ideas and potential experiments here.",
    ]

    return BriefModel(
        project_title=summary.project_title,
        project_description=description,
        purpose=purpose,
        expected_outcomes=outcomes,
        business_model=business_model,
        success_metrics=summary.success_metrics or outcomes,
        target_users=summary.target_users or ["Define primary users with the intake agent."],
        risks=risks,
        timeline=timeline,
        opportunity_explorer=opportunity,
        suggested_reads=suggested_reads,
        ideas_board=ideas_board,
        documents=summary.documents,
    )


def _coalesce(candidates: List[str | None], default: str) -> str:
    for candidate in candidates:
        if candidate and candidate.strip():
            return candidate.strip()
    return default


