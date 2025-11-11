"""Routes for coordinating project brief generation."""

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, model_validator

from app.dependencies.mongo import get_database
from app.services.agents_client import AgentsClient, get_agents_client

router = APIRouter()


class ConversationTurn(BaseModel):
    """Represents a single conversational message."""

    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(..., min_length=1)


class DocumentReference(BaseModel):
    """Metadata about a document shared during intake."""

    id: str = Field(default_factory=str)
    name: str = Field(..., min_length=1)
    url: str | None = None
    notes: str | None = None


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
        if self.conversation and self.prompt:
            return self
        if self.prompt and not self.conversation:
            self.conversation = [ConversationTurn(role="user", content=self.prompt)]
        return self


class BriefResponse(BaseModel):
    """Structured brief response returned to clients."""

    summary: dict[str, Any]
    brief: dict[str, Any]
    follow_up_questions: list[str]
    thread_id: str
    run_id: str


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

    document = {
        "conversation": conversation_payload,
        "documents": document_payload,
        "summary": workflow_output.get("summary", {}),
        "brief": workflow_output.get("brief", {}),
        "follow_up_questions": workflow_output.get("follow_up_questions", []),
        "thread_id": workflow_output.get("thread_id"),
        "created_at": datetime.now(timezone.utc),
    }

    result = await database["brief_runs"].insert_one(document)

    return BriefResponse(
        summary=document["summary"],
        brief=document["brief"],
        follow_up_questions=document["follow_up_questions"],
        thread_id=document["thread_id"],
        run_id=str(result.inserted_id),
    )

