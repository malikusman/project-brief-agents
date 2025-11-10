"""CLI entrypoint for running the agents workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_agents.service import run_project_brief_workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute the Project Brief LangGraph workflow."
    )
    parser.add_argument(
        "--input",
        "-i",
        dest="input_text",
        type=str,
        required=False,
        help="User-provided project description text.",
    )
    parser.add_argument(
        "--input-file",
        dest="input_file",
        type=Path,
        required=False,
        help="Path to a file containing the user prompt.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.input_text:
        user_input = args.input_text
    elif args.input_file:
        user_input = args.input_file.read_text(encoding="utf-8")
    else:
        raise SystemExit("Provide --input or --input-file.")

    state = run_project_brief_workflow(user_input)
    print(json.dumps(state, indent=2, ensure_ascii=False))  # noqa: T201


if __name__ == "__main__":
    main()


