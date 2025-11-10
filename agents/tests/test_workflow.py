"""Tests for the LangGraph project brief workflow."""

from project_agents.service import run_project_brief_workflow


def test_workflow_returns_summary_and_brief() -> None:
    """Workflow should generate summary and brief placeholders."""

    result = run_project_brief_workflow("Test project details")

    assert "summary" in result
    assert "brief" in result
    assert result["summary"]["project_title"] == "Untitled Project"
    assert isinstance(result["brief"]["expected_outcomes"], list)


