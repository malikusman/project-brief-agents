"""Routes for coordinating project brief generation."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, model_validator

from app.dependencies.mongo import get_database
from app.models import AgentRunModel, BriefModel, ConversationTurn, DocumentReference, SummaryModel
from app.services.agents_client import AgentsClient, get_agents_client

router = APIRouter()


class BriefRequest(BaseModel):
    """Payload for initiating a brief generation run."""

    prompt: str | None = Field(
        default=None, description="Initial project context if conversation not provided."
    )
    conversation: list[ConversationTurn] | None = None
    documents: list[DocumentReference] = Field(default_factory=list)
    thread_id: str | None = Field(
        default=None, description="Optional thread identifier for LangGraph checkpoints."
    )

    @model_validator(mode="after")
    def ensure_conversation(self) -> "BriefRequest":
        if not self.conversation and not self.prompt:
            raise ValueError("Either prompt or conversation must be provided.")
        if self.prompt and not self.conversation:
            self.conversation = [ConversationTurn(role="user", content=self.prompt)]
        return self


class BriefResponse(BaseModel):
    """Structured brief response returned to clients."""

    summary: SummaryModel
    brief: BriefModel
    follow_up_questions: list[str]
    thread_id: str
    run_id: str
    assistant_message: str


@router.post(
    "/briefs/run",
    response_model=BriefResponse,
    status_code=status.HTTP_200_OK,
)
async def run_brief_generation(
    payload: BriefRequest,
    agents_client: AgentsClient = Depends(get_agents_client),
    database=Depends(get_database),
) -> BriefResponse:
    """Trigger the agents workflow, persist the result, and return the structured brief."""

    conversation_payload = [turn.model_dump() for turn in payload.conversation or []]
    document_payload = [doc.model_dump() for doc in payload.documents]

    workflow_output = await agents_client.run_workflow(
        conversation=conversation_payload,
        documents=document_payload,
        thread_id=payload.thread_id,
    )

    agent_model = AgentRunModel.model_validate(workflow_output)
    document = {
        "conversation": conversation_payload,
        "documents": document_payload,
        "summary": agent_model.summary.model_dump(),
        "brief": agent_model.brief.model_dump(),
        "follow_up_questions": agent_model.follow_up_questions,
        "thread_id": agent_model.thread_id,
        "assistant_message": agent_model.assistant_message,
        "created_at": datetime.now(timezone.utc),
    }

    result = await database["brief_runs"].insert_one(document)

    return BriefResponse(
        summary=agent_model.summary,
        brief=agent_model.brief,
        follow_up_questions=agent_model.follow_up_questions,
        thread_id=agent_model.thread_id,
        assistant_message=agent_model.assistant_message,
        run_id=str(result.inserted_id),
    )

