"""HTTP client for interacting with the LangGraph agents service."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class AgentsClient:
    """Thin wrapper around the agents workflow endpoint."""

    def __init__(self, base_url: str, timeout_seconds: int) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    async def run_workflow(self, prompt: str) -> dict[str, Any]:
        """Invoke the workflow run endpoint."""

        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout_seconds,
        ) as client:
            response = await client.post(
                "/workflow/run",
                json={"prompt": prompt},
            )
            response.raise_for_status()
            return response.json()


async def get_agents_client() -> AgentsClient:
    """FastAPI dependency factory for AgentsClient."""

    settings = get_settings()
    return AgentsClient(
        base_url=settings.agents_base_url,
        timeout_seconds=settings.agents_timeout_seconds,
    )

