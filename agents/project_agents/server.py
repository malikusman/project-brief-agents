"""FastAPI service exposing LangGraph workflow endpoints."""

from fastapi import FastAPI, status
from pydantic import BaseModel

from project_agents.service import run_project_brief_workflow


class WorkflowRequest(BaseModel):
    """Payload for executing the project brief workflow."""

    prompt: str


class WorkflowResponse(BaseModel):
    """Structured response returning generated summary and brief."""

    summary: dict[str, object]
    brief: dict[str, object]


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

    state = run_project_brief_workflow(payload.prompt)
    return WorkflowResponse(
        summary=state.get("summary", {}),
        brief=state.get("brief", {}),
    )


