"""Workflow node implementations."""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from project_agents.brief.formatter import build_brief
from project_agents.graphs.state import ProjectState
from project_agents.intake.analyzer import analyze_prompt
from project_agents.intake.question_queue import get_next_questions, update_queue_from_summary
from project_agents.intake.tone import generate_follow_up_message
from project_agents.models import LovableBrief, SummaryPayload
from project_agents.utils.context_window import get_recent_messages


def build_intake_node() -> RunnableLambda:
    """Return a runnable that summarizes intake conversations."""

    def _run(state: ProjectState) -> ProjectState:
        conversation = state.get("conversation", [])
        documents = state.get("documents", [])
        
        # Use context window utility to keep only last N messages (default: 15)
        prompt_text = get_recent_messages(conversation)
        
        # Comment out document processing for now
        # document_texts = [doc.get("text", "") for doc in documents if doc.get("text")]
        # prompt_segments = user_messages + document_texts
        # prompt_text = "\n".join(segment for segment in prompt_segments if segment)
        # document_names = [doc.get("name", "") or doc.get("id", "") for doc in documents] if documents else []
        document_names = []  # Documents disabled for now

        summary_payload, question_queue, insights = analyze_prompt(prompt_text, document_names)
        
        # Get existing queue from state (if any)
        existing_queue = state.get("question_queue", [])
        previous_summary = None
        if state.get("summary"):
            try:
                previous_summary = SummaryPayload(**state.get("summary", {}))
            except Exception:
                pass
        
        # Update queue based on new summary (removes answered questions)
        updated_queue = update_queue_from_summary(previous_summary, summary_payload, existing_queue)
        
        # Select 1-2 questions to ask (highest priority, unanswered)
        current_questions = get_next_questions(updated_queue, max_questions=2)
        
        # Convert to list of strings for tone.py (backward compatibility)
        follow_up_strings = [q["question"] for q in current_questions]
        
        assistant_text = generate_follow_up_message(summary_payload, follow_up_strings, insights)
        summary_message = AIMessage(content=assistant_text, name="intake_agent")

        return {
            "messages": state.get("messages", []) + [summary_message],
            "conversation": conversation,
            "documents": [],  # Documents disabled for now
            "summary": summary_payload.model_dump(),
            "question_queue": updated_queue,
            "current_questions": current_questions,
            "follow_up_questions": follow_up_strings,  # Keep for backward compatibility
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
