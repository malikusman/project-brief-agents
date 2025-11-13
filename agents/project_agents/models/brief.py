"""Typed schema describing summaries and Lovable-style briefs."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SummaryPayload(BaseModel):
    """Structured summary captured by the intake agent."""

    project_title: str = Field(default="Untitled Project")
    problem: Optional[str] = Field(default=None)
    solution: Optional[str] = Field(default=None)
    target_users: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    timeline: Optional[str] = Field(default=None)
    resources: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    opportunity_areas: List[str] = Field(default_factory=list)


class LovableBrief(BaseModel):
    """Final Lovable-style brief delivered to the frontend/backend."""

    project_title: str = Field(default="Untitled Project")
    project_description: str = Field(
        default="This section will be expanded as the intake flow gathers more context."
    )
    purpose: str = Field(
        default="Clarify the project's purpose once additional details are collected."
    )
    expected_outcomes: List[str] = Field(default_factory=list)
    business_model: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(
        default_factory=lambda: [
            "Surface constraints, risks, and dependencies during intake."
        ]
    )
    timeline: str = Field(default="Timeline not specified yet.")
    target_users: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    opportunity_areas: List[str] = Field(default_factory=list)
    suggested_reads: List[str] = Field(default_factory=list)
    ideas_board: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)


class BriefPayload(BaseModel):
    """Combined payload returned by the agents service."""

    summary: SummaryPayload
    brief: LovableBrief
    follow_up_questions: List[str]
    thread_id: str
    assistant_message: str


class IntakeInsights(BaseModel):
    """Metadata about captured and missing summary fields."""

    captured_fields: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)


class DocumentReference(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    notes: Optional[str] = None
    text: Optional[str] = None
