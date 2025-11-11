"""Workflow node implementations."""

from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from project_agents.brief.formatter import build_brief
from project_agents.graphs.state import DocumentReference, ProjectState
from project_agents.intake.analyzer import analyze_prompt
from project_agents.models import SummaryModel


def build_intake_node() -> RunnableLambda:
    """Return a runnable that summarizes intake conversations."""

    def _run(state: ProjectState) -> ProjectState:
        conversation = state.get("conversation", [])
        documents = state.get("documents", [])
        user_messages = [
            turn["content"]
            for turn in conversation
            if turn.get("role", "user").lower() == "user"
        ]
        prompt_text = "\n".join(user_messages)
        document_names = [doc.get("name", "") for doc in documents]

        summary_model, follow_ups = analyze_prompt(prompt_text, document_names)

        summary_message = AIMessage(
            content="Intake summary prepared with "
            f"{len(follow_ups)} follow-up question(s).",
            name="intake_agent",
        )

        return {
            "messages": state.get("messages", []) + [summary_message],
            "conversation": conversation,
            "documents": documents,
            "summary": summary_model.model_dump(),
            "follow_up_questions": follow_ups,
        }

    return RunnableLambda(_run)


def build_brief_node() -> RunnableLambda:
    """Return a runnable that structures the Lovable-style brief."""

    def _run(state: ProjectState) -> ProjectState:
        summary_dict = state.get("summary", {})
        summary_model = SummaryModel(**summary_dict)
        brief = build_brief(summary_model)
        message = AIMessage(content="Project brief structured.", name="brief_agent")
        return {
            "messages": state.get("messages", []) + [message],
            "brief": brief.model_dump(),
        }

    return RunnableLambda(_run)

