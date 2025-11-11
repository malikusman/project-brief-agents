"""Tests for the LangGraph project brief workflow."""

from project_agents.service import run_project_brief_workflow


def test_workflow_returns_summary_and_brief() -> None:
    """Workflow should generate summary and brief placeholders."""

    conversation = [
        {"role": "user", "content": "We are launching a mobile app to help students track study goals."},
        {"role": "user", "content": "Our target users are college freshmen and success is measured by daily active usage."},
    ]
    documents = [
        {"id": "spec-1", "name": "Discovery notes", "url": None, "notes": None}
    ]

    result = run_project_brief_workflow(conversation, documents=documents)

    assert "summary" in result
    assert "brief" in result
    assert result["summary"]["project_title"]
    assert isinstance(result["follow_up_questions"], list)
    assert isinstance(result["brief"]["expected_outcomes"], list)

