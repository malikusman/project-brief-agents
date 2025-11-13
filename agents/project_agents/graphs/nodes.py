"""Workflow node implementations."""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from project_agents.brief.formatter import build_brief
from project_agents.graphs.state import ProjectState
from project_agents.intake.analyzer import analyze_prompt
from project_agents.intake.tone import generate_follow_up_message
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

        summary_payload, follow_ups, insights = analyze_prompt(prompt_text, document_names)
        assistant_text = generate_follow_up_message(summary_payload, follow_ups, insights)
        summary_message = AIMessage(content=assistant_text, name="intake_agent")

        return {
            "messages": state.get("messages", []) + [summary_message],
            "conversation": conversation,
            "documents": documents,
            "summary": summary_payload.model_dump(),
            "follow_up_questions": follow_ups,
            "assistant_message": assistant_text,
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
            "assistant_message": state.get("assistant_message", ""),
        }

    return RunnableLambda(_run)
