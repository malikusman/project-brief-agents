"""Shared data models for summaries and briefs."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class SummaryModel(BaseModel):
    project_title: str = Field(default="Untitled Project")
    problem: str | None = None
    solution: str | None = None
    target_users: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    timeline: str | None = None
    resources: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)


class BriefModel(BaseModel):
    project_title: str
    project_description: str
    purpose: str
    expected_outcomes: List[str]
    business_model: List[str]
    success_metrics: List[str]
    target_users: List[str]
    risks: List[str]
    timeline: str
    opportunity_explorer: List[str]
    suggested_reads: List[str]
    ideas_board: List[str]
    documents: List[str]


class AgentRunModel(BaseModel):
    summary: SummaryModel
    brief: BriefModel
    follow_up_questions: List[str]
    thread_id: str
