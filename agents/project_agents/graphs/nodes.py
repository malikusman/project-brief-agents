"""Workflow node implementations."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableLambda

from project_agents.config.settings import get_settings
from project_agents.graphs.state import ProjectState
from project_agents.prompts.loaders import load_prompt


def build_intake_node() -> RunnableLambda:
    """Return a runnable that simulates the intake agent."""

    settings = get_settings()
    system_prompt = load_prompt(settings.intake_system_prompt_path)

    def _run(state: ProjectState) -> ProjectState:
        messages = list(state.get("messages", []))
        messages.insert(
            0, SystemMessage(content=system_prompt, name="intake_directive")
        )
        summary = {
            "project_title": "Untitled Project",
            "goals": [
                "Placeholder goal until intake flow is implemented.",
            ],
            "notes": [m.content for m in state.get("messages", [])],
        }
        messages.append(AIMessage(content="Summary drafted.", name="intake_agent"))
        return {"messages": messages, "summary": summary}

    return RunnableLambda(_run)


def build_brief_node() -> RunnableLambda:
    """Return a runnable that simulates the brief-generation agent."""

    settings = get_settings()
    system_prompt = load_prompt(settings.brief_system_prompt_path)

    def _run(state: ProjectState) -> ProjectState:
        messages = list(state.get("messages", []))
        messages.append(
            SystemMessage(content=system_prompt, name="brief_directive")
        )

        summary = state.get("summary", {})
        brief: dict[str, Any] = {
            "project_description": summary.get(
                "project_title", "Draft project description pending intake."
            ),
            "purpose": "Purpose to be refined once agents run against user data.",
            "expected_outcomes": [
                "Outcome placeholder – replace with generated content."
            ],
            "business_model": [
                "Business model placeholder – integrate with Agent #2 output."
            ],
        }

        messages.append(AIMessage(content="Brief drafted.", name="brief_agent"))
        return {"messages": messages, "brief": brief}

    return RunnableLambda(_run)


