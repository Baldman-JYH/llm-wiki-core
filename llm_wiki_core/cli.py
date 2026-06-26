from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
import json
import sys
from typing import Any

from llm_wiki_core import __version__
from llm_wiki_core.operations.continue_ import continue_wiki
from llm_wiki_core.operations.detect_transport import detect_transport
from llm_wiki_core.operations.ingest import ingest_source
from llm_wiki_core.operations.init import init_vault
from llm_wiki_core.operations.lint import lint_wiki
from llm_wiki_core.operations.query import query_wiki
from llm_wiki_core.operations.save import save_insight
from llm_wiki_core.operations.status import status_wiki


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-wiki",
        description="Neutral LLM Wiki core command line entry.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"llm-wiki-core {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize an LLM Wiki vault.")
    init_parser.add_argument("vault", help="Path to the vault root.")
    init_parser.add_argument("--purpose", required=True, help="One-sentence vault purpose.")
    _add_json_option(init_parser)

    transport_parser = subparsers.add_parser(
        "detect-transport",
        help="Detect available LLM Wiki transports.",
    )
    transport_parser.add_argument("vault", help="Path to the vault root.")
    transport_parser.add_argument("--force", action="store_true", help="Refresh the transport snapshot.")
    _add_json_option(transport_parser)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest one raw source into the wiki.")
    ingest_parser.add_argument("vault", help="Path to the vault root.")
    ingest_parser.add_argument("source", help="Vault-relative raw source path under .raw/.")
    ingest_parser.add_argument("--force", action="store_true", help="Re-ingest even when the source is unchanged.")
    _add_json_option(ingest_parser)

    query_parser = subparsers.add_parser("query", help="Query the local LLM Wiki.")
    query_parser.add_argument("vault", help="Path to the vault root.")
    query_parser.add_argument("question", help="Question to answer from the wiki.")
    query_parser.add_argument("--depth", default="standard", help="Query depth. MVP supports standard.")
    _add_json_option(query_parser)

    save_parser = subparsers.add_parser("save", help="Save durable content into the wiki.")
    save_parser.add_argument("vault", help="Path to the vault root.")
    save_parser.add_argument("--content", required=True, help="Content to save.")
    save_parser.add_argument("--title", help="Optional page title.")
    save_parser.add_argument("--target-type", default="question", choices=["question", "concept"])
    _add_json_option(save_parser)

    lint_parser = subparsers.add_parser("lint", help="Check LLM Wiki health.")
    lint_parser.add_argument("vault", help="Path to the vault root.")
    lint_parser.add_argument("--no-report", action="store_true", help="Do not write a lint report.")
    _add_json_option(lint_parser)

    status_parser = subparsers.add_parser("status", help="Report LLM Wiki vault status.")
    status_parser.add_argument("vault", help="Path to the vault root.")
    _add_json_option(status_parser)

    continue_parser = subparsers.add_parser("continue", help="Resume recent LLM Wiki context.")
    continue_parser.add_argument("vault", help="Path to the vault root.")
    _add_json_option(continue_parser)
    return parser


def _add_json_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print one machine-readable JSON object.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = _execute(args)
    except Exception as error:
        return _print_error(args, error)

    if result is None:
        return 0
    if getattr(args, "json", False):
        print(json.dumps(_to_jsonable(result), ensure_ascii=False, sort_keys=True))
        return 0

    _print_text_result(args.command, result)
    return 0


def _execute(args: argparse.Namespace) -> object | None:
    if args.command == "init":
        return init_vault(args.vault, purpose=args.purpose, adapter="codex")

    if args.command == "detect-transport":
        return detect_transport(args.vault, force=args.force)

    if args.command == "ingest":
        return ingest_source(args.vault, args.source, force=args.force)

    if args.command == "query":
        return query_wiki(args.vault, args.question, depth=args.depth)

    if args.command == "save":
        return save_insight(
            args.vault,
            content=args.content,
            title=args.title,
            target_type=args.target_type,
        )

    if args.command == "lint":
        return lint_wiki(args.vault, write_report=not args.no_report)

    if args.command == "status":
        return status_wiki(args.vault)

    if args.command == "continue":
        return continue_wiki(args.vault)

    return None


def _print_text_result(command: str, result: object) -> None:
    if command == "init":
        print(f"{result.operation} {result.status}")
        print(f"created: {len(result.files_created)}")
        print(f"skipped: {len(result.files_skipped)}")
        print(f"next: {result.next_suggested_action}")

    if command == "detect-transport":
        print(f"{result.operation} {result.status}")
        print(f"preferred: {result.snapshot.preferred}")
        print(f"snapshot: {result.snapshot_path}")
        print(f"next: {result.next_suggested_action}")

    if command == "ingest":
        print(f"{result.operation} {result.status}")
        print(f"source: {result.source_path}")
        print(f"created: {len(result.files_created)}")
        print(f"updated: {len(result.files_updated)}")
        print(f"skipped: {len(result.files_skipped)}")
        print(f"next: {result.next_suggested_action}")

    if command == "query":
        print(f"{result.operation} {result.status}")
        print(result.answer)
        if result.gaps:
            print("gaps:")
            for gap in result.gaps:
                print(f"- {gap}")

    if command == "save":
        print(f"{result.operation} {result.status}")
        print(f"page: {result.page_path}")
        print(f"created: {len(result.files_created)}")
        print(f"updated: {len(result.files_updated)}")
        print(f"next: {result.next_suggested_action}")

    if command == "lint":
        print(f"{result.operation} {result.status}")
        for severity in ("blocker", "high", "medium", "low"):
            print(f"{severity}: {result.counts[severity]}")
        if result.report_path:
            print(f"report: {result.report_path}")

    if command == "status":
        print(f"{result.operation} {result.status}")
        print(f"initialized: {str(result.initialized).lower()}")
        print(f"sources: {result.source_count}")
        print(f"preferred transport: {result.preferred_transport or 'unknown'}")
        if result.recent_log_entry:
            print(f"recent log: {result.recent_log_entry}")
        if result.missing_required_paths:
            print("missing:")
            for path in result.missing_required_paths:
                print(f"- {path}")
        print(f"next: {result.next_suggested_action}")

    if command == "continue":
        print(f"{result.operation} {result.status}")
        print(f"files read: {len(result.files_read)}")
        if result.recent_log_entries:
            print("recent log:")
            for entry in result.recent_log_entries:
                print(f"- {entry}")
        print(f"next: {result.next_suggested_action}")


def _print_error(args: argparse.Namespace, error: Exception) -> int:
    operation = args.command or "llm-wiki"
    if getattr(args, "json", False):
        payload = {
            "operation": operation,
            "status": "error",
            "error": {
                "type": type(error).__name__,
                "message": str(error),
            },
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{operation} error", file=sys.stderr)
        print(f"error: {error}", file=sys.stderr)
    return 1


def _to_jsonable(value: object) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
