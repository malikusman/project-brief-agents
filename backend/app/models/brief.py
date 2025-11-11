"""Shared brief and summary schemas."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class DocumentReference(BaseModel):
    id: str = Field(default_factory=str)
    name: str = Field(..., min_length=1)
    url: str | None = None
    notes: str | None = None


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
    opportunity_areas: List[str] = Field(default_factory=list)


class BriefModel(BaseModel):
    project_title: str
    project_description: str
    purpose: str
    expected_outcomes: List[str]
    business_model: List[str]
    constraints: List[str]
    timeline: str
    target_users: List[str]
    documents: List[str]
    opportunity_areas: List[str]
    suggested_reads: List[str]
    ideas_board: List[str]
    success_metrics: List[str]


class AgentRunModel(BaseModel):
    summary: SummaryModel
    brief: BriefModel
    follow_up_questions: List[str]
    thread_id: str


class ConversationTurn(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str
