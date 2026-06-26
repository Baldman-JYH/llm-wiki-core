from __future__ import annotations

import argparse

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

    transport_parser = subparsers.add_parser(
        "detect-transport",
        help="Detect available LLM Wiki transports.",
    )
    transport_parser.add_argument("vault", help="Path to the vault root.")
    transport_parser.add_argument("--force", action="store_true", help="Refresh the transport snapshot.")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest one raw source into the wiki.")
    ingest_parser.add_argument("vault", help="Path to the vault root.")
    ingest_parser.add_argument("source", help="Vault-relative raw source path under .raw/.")
    ingest_parser.add_argument("--force", action="store_true", help="Re-ingest even when the source is unchanged.")

    query_parser = subparsers.add_parser("query", help="Query the local LLM Wiki.")
    query_parser.add_argument("vault", help="Path to the vault root.")
    query_parser.add_argument("question", help="Question to answer from the wiki.")
    query_parser.add_argument("--depth", default="standard", help="Query depth. MVP supports standard.")

    save_parser = subparsers.add_parser("save", help="Save durable content into the wiki.")
    save_parser.add_argument("vault", help="Path to the vault root.")
    save_parser.add_argument("--content", required=True, help="Content to save.")
    save_parser.add_argument("--title", help="Optional page title.")
    save_parser.add_argument("--target-type", default="question", choices=["question", "concept"])

    lint_parser = subparsers.add_parser("lint", help="Check LLM Wiki health.")
    lint_parser.add_argument("vault", help="Path to the vault root.")
    lint_parser.add_argument("--no-report", action="store_true", help="Do not write a lint report.")

    status_parser = subparsers.add_parser("status", help="Report LLM Wiki vault status.")
    status_parser.add_argument("vault", help="Path to the vault root.")

    continue_parser = subparsers.add_parser("continue", help="Resume recent LLM Wiki context.")
    continue_parser.add_argument("vault", help="Path to the vault root.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        result = init_vault(args.vault, purpose=args.purpose, adapter="codex")
        print(f"{result.operation} {result.status}")
        print(f"created: {len(result.files_created)}")
        print(f"skipped: {len(result.files_skipped)}")
        print(f"next: {result.next_suggested_action}")

    if args.command == "detect-transport":
        result = detect_transport(args.vault, force=args.force)
        print(f"{result.operation} {result.status}")
        print(f"preferred: {result.snapshot.preferred}")
        print(f"snapshot: {result.snapshot_path}")
        print(f"next: {result.next_suggested_action}")

    if args.command == "ingest":
        result = ingest_source(args.vault, args.source, force=args.force)
        print(f"{result.operation} {result.status}")
        print(f"source: {result.source_path}")
        print(f"created: {len(result.files_created)}")
        print(f"updated: {len(result.files_updated)}")
        print(f"skipped: {len(result.files_skipped)}")
        print(f"next: {result.next_suggested_action}")

    if args.command == "query":
        result = query_wiki(args.vault, args.question, depth=args.depth)
        print(f"{result.operation} {result.status}")
        print(result.answer)
        if result.gaps:
            print("gaps:")
            for gap in result.gaps:
                print(f"- {gap}")

    if args.command == "save":
        result = save_insight(
            args.vault,
            content=args.content,
            title=args.title,
            target_type=args.target_type,
        )
        print(f"{result.operation} {result.status}")
        print(f"page: {result.page_path}")
        print(f"created: {len(result.files_created)}")
        print(f"updated: {len(result.files_updated)}")
        print(f"next: {result.next_suggested_action}")

    if args.command == "lint":
        result = lint_wiki(args.vault, write_report=not args.no_report)
        print(f"{result.operation} {result.status}")
        for severity in ("blocker", "high", "medium", "low"):
            print(f"{severity}: {result.counts[severity]}")
        if result.report_path:
            print(f"report: {result.report_path}")

    if args.command == "status":
        result = status_wiki(args.vault)
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

    if args.command == "continue":
        result = continue_wiki(args.vault)
        print(f"{result.operation} {result.status}")
        print(f"files read: {len(result.files_read)}")
        if result.recent_log_entries:
            print("recent log:")
            for entry in result.recent_log_entries:
                print(f"- {entry}")
        print(f"next: {result.next_suggested_action}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
