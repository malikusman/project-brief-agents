"""Routes for coordinating project brief generation."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.dependencies.mongo import get_database
from app.services.agents_client import AgentsClient, get_agents_client

router = APIRouter()


class BriefRequest(BaseModel):
    """Payload for initiating a brief generation run."""

    prompt: str = Field(..., min_length=1, description="User supplied project context.")


class BriefResponse(BaseModel):
    """Structured brief response returned to clients."""

    summary: dict[str, Any]
    brief: dict[str, Any]
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

    workflow_output = await agents_client.run_workflow(prompt=payload.prompt)

    document = {
        "prompt": payload.prompt,
        "summary": workflow_output.get("summary", {}),
        "brief": workflow_output.get("brief", {}),
        "created_at": datetime.now(timezone.utc),
    }

    result = await database["brief_runs"].insert_one(document)

    return BriefResponse(
        summary=document["summary"],
        brief=document["brief"],
        run_id=str(result.inserted_id),
    )

