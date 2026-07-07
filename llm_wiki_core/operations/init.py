from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from llm_wiki_core.vault.scaffold import get_organization_definition


@dataclass(frozen=True)
class OperationResult:
    operation: str
    status: str
    organization: str = "generic"
    files_created: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def init_vault(
    vault_root: str | Path,
    purpose: str,
    adapter: str = "codex",
    organization: str = "generic",
) -> OperationResult:
    definition = get_organization_definition(organization)
    root = Path(vault_root)
    if root.exists() and not root.is_dir():
        raise NotADirectoryError(f"Vault root is not a directory: {root}")

    root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    date = timestamp[:10]
    files_created: list[str] = []
    files_skipped: list[str] = []

    for relative in definition.required_directories:
        (root / relative).mkdir(parents=True, exist_ok=True)

    _write_json_if_missing(
        root / ".raw" / ".manifest.json",
        {
            "schema_version": 1,
            "updated": timestamp,
            "sources": {},
        },
        root,
        files_created,
        files_skipped,
    )

    seed_pages = {
        root / page.relative_path: page.render(
            created=date,
            updated=timestamp,
            purpose=purpose,
        )
        for page in definition.seed_pages
    }
    for path, content in seed_pages.items():
        _write_text_if_missing(path, content, root, files_created, files_skipped)

    if adapter == "codex":
        _write_text_if_missing(
            root / "AGENTS.md",
            _agents_page(purpose),
            root,
            files_created,
            files_skipped,
        )

    return OperationResult(
        operation="init",
        status="success",
        organization=definition.name,
        files_created=files_created,
        files_skipped=files_skipped,
        warnings=[],
        next_suggested_action="Add raw sources under .raw/ and run ingest.",
    )


def _write_json_if_missing(
    path: Path,
    data: dict[str, object],
    root: Path,
    files_created: list[str],
    files_skipped: list[str],
) -> None:
    if path.exists():
        files_skipped.append(_relative_path(path, root))
        return

    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    files_created.append(_relative_path(path, root))


def _write_text_if_missing(
    path: Path,
    content: str,
    root: Path,
    files_created: list[str],
    files_skipped: list[str],
) -> None:
    if path.exists():
        files_skipped.append(_relative_path(path, root))
        return

    path.write_text(content, encoding="utf-8")
    files_created.append(_relative_path(path, root))


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _agents_page(purpose: str) -> str:
    return (
        "# LLM Wiki Agent Instructions\n\n"
        + f"Purpose: {purpose}\n\n"
        + "Use this vault according to the LLM Wiki pattern:\n\n"
        + "- Treat `.raw/` as immutable source material.\n"
        + "- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.\n"
        + "- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.\n"
        + "- Follow the operation contracts in `docs/operation-contract.md` when available.\n"
        + "\n"
        + "## MVP Commands\n\n"
        + "Use the local `llm-wiki` CLI when available:\n\n"
        + "- `llm-wiki init <vault> --purpose \"...\"`\n"
        + "- `llm-wiki detect-transport <vault>`\n"
        + "- `llm-wiki status <vault>`\n"
        + "- `llm-wiki continue <vault>`\n"
        + "- `llm-wiki ingest <vault> <source-under-.raw>`\n"
        + "- `llm-wiki query <vault> \"<question>\"`\n"
        + "- `llm-wiki save <vault> --title \"...\" --content \"...\"`\n"
        + "- `llm-wiki lint <vault>`\n"
        + "\n"
        + "Natural language triggers should map to the same operations:\n\n"
        + "- \"set up wiki\" -> init\n"
        + "- \"check transport\" -> detect-transport\n"
        + "- \"check wiki status\" -> status\n"
        + "- \"continue wiki\" -> continue\n"
        + "- \"resume wiki context\" -> continue\n"
        + "- \"ingest this source\" -> ingest\n"
        + "- \"what does the wiki know about X\" -> query\n"
        + "- \"save this insight\" -> save\n"
        + "- \"lint the wiki\" -> lint\n"
    )
