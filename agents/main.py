"""CLI entrypoint for running the agents workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_agents.service import run_project_brief_workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Project Brief agents runner. Default mode starts the API server."
    )
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI service.")
    serve_parser.add_argument(
        "--host", default="0.0.0.0", help="Host interface for the API server."
    )
    serve_parser.add_argument(
        "--port", type=int, default=8080, help="Port for the API server."
    )

    run_parser = subparsers.add_parser(
        "run", help="Execute the workflow locally and print JSON output."
    )
    run_parser.add_argument(
        "--input",
        "-i",
        dest="input_text",
        type=str,
        required=False,
        help="User-provided project description text.",
    )
    run_parser.add_argument(
        "--input-file",
        dest="input_file",
        type=Path,
        required=False,
        help="Path to a file containing the user prompt.",
    )

    parser.set_defaults(command="serve")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "serve":
        import uvicorn

        uvicorn.run(
            "project_agents.server:app",
            host=args.host,
            port=args.port,
            reload=False,
        )
        return

    input_text = args.input_text
    if not input_text and args.input_file:
        input_text = args.input_file.read_text(encoding="utf-8")

    if not input_text:
        raise SystemExit("Provide --input or --input-file.")

    state = run_project_brief_workflow(input_text)
    print(json.dumps(state, indent=2, ensure_ascii=False))  # noqa: T201


if __name__ == "__main__":
    main()


