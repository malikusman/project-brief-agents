"""FastAPI service exposing LangGraph workflow endpoints."""

from typing import Literal, Optional

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

from project_agents.models import BriefPayload, LovableBrief, SummaryPayload
from project_agents.service import run_project_brief_workflow


class ConversationTurn(BaseModel):
    """Single message exchanged during the intake conversation."""

    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(..., min_length=1)


class DocumentReference(BaseModel):
    """Metadata describing a document shared during intake."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    url: Optional[str] = None
    notes: Optional[str] = None


class WorkflowRequest(BaseModel):
    """Payload for executing the project brief workflow."""

    conversation: list[ConversationTurn] = Field(..., min_length=1)
    documents: list[DocumentReference] = Field(default_factory=list)
    thread_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Structured response returning generated summary and brief."""

    summary: SummaryPayload
    brief: LovableBrief
    follow_up_questions: list[str]
    thread_id: str


app = FastAPI(title="Project Brief Agents Service")


@app.get("/health/live", status_code=status.HTTP_200_OK)
async def live() -> dict[str, str]:
    """Liveness probe."""

    return {"status": "ok"}


@app.post(
    "/workflow/run",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
)
async def run_workflow(payload: WorkflowRequest) -> WorkflowResponse:
    """Execute the LangGraph workflow and return structured results."""

    state = run_project_brief_workflow(
        conversation=[turn.model_dump() for turn in payload.conversation],
        documents=[doc.model_dump() for doc in payload.documents],
        thread_id=payload.thread_id,
    )
    agent_payload = BriefPayload(**state)
    return WorkflowResponse(
        summary=agent_payload.summary,
        brief=agent_payload.brief,
        follow_up_questions=agent_payload.follow_up_questions,
        thread_id=agent_payload.thread_id,
    )
