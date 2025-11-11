"""Shape intake summaries into Lovable-style brief sections."""

from __future__ import annotations

from project_agents.models import LovableBrief, SummaryPayload


def build_brief(summary: SummaryPayload) -> LovableBrief:
    """Convert an intake summary into the Lovable brief layout."""

    description = summary.problem or summary.solution or (
        "This brief will be expanded as the intake conversation gathers more context."
    )
    purpose = summary.solution or "Clarify the project's purpose once additional details are collected."

    expected_outcomes = summary.success_metrics or [
        "Define success metrics that indicate adoption and impact.",
        "Identify measurable outcomes aligned with strategic goals.",
    ]

    business_model = summary.resources or [
        "List revenue streams, partnerships, or resource requirements.",
        "Outline go-to-market considerations and support needs.",
    ]

    constraints = summary.constraints or [
        "Surface constraints, risks, and dependencies during intake."
    ]

    timeline = summary.timeline or "Timeline not specified yet."

    opportunity = summary.opportunity_areas or [
        "Explore adjacent opportunities uncovered during discovery.",
        "Validate market demand and differentiation opportunities.",
    ]

    suggested_reads = [
        "Add foundational research or industry reports to guide the team.",
    ]

    ideas_board = [
        "Capture brainstorm ideas and potential experiments here.",
    ]

    return LovableBrief(
        project_title=summary.project_title,
        project_description=description,
        purpose=purpose,
        expected_outcomes=expected_outcomes,
        business_model=business_model,
        constraints=constraints,
        timeline=timeline,
        target_users=summary.target_users or [
            "Define primary users with the intake agent."
        ],
        documents=summary.documents,
        opportunity_areas=opportunity,
        suggested_reads=suggested_reads,
        ideas_board=ideas_board,
        success_metrics=summary.success_metrics or expected_outcomes,
    )
