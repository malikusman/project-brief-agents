"""Workflow node implementations."""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from project_agents.brief.formatter import build_brief
from project_agents.graphs.state import ProjectState
from project_agents.intake.analyzer import analyze_prompt
from project_agents.models import LovableBrief, SummaryPayload


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

        summary_payload, follow_ups = analyze_prompt(prompt_text, document_names)

        summary_message = AIMessage(
            content="Intake summary prepared with "
            f"{len(follow_ups)} follow-up question(s).",
            name="intake_agent",
        )

        return {
            "messages": state.get("messages", []) + [summary_message],
            "conversation": conversation,
            "documents": documents,
            "summary": summary_payload.model_dump(),
            "follow_up_questions": follow_ups,
        }

    return RunnableLambda(_run)


def build_brief_node() -> RunnableLambda:
    """Return a runnable that structures the Lovable-style brief."""

    def _run(state: ProjectState) -> ProjectState:
        summary_dict = state.get("summary", {})
        summary_payload = SummaryPayload(**summary_dict)
        brief_payload: LovableBrief = build_brief(summary_payload)
        message = AIMessage(content="Project brief structured.", name="brief_agent")
        return {
            "messages": state.get("messages", []) + [message],
            "brief": brief_payload.model_dump(),
        }

    return RunnableLambda(_run)
