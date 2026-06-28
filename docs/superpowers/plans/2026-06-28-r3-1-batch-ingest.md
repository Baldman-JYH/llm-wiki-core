# R3.1 Batch Ingest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a conservative local Markdown batch ingest command that reuses the existing single-source ingest behavior.

**Architecture:** Implement one neutral operation, `ingest_batch(...)`, that validates a `.raw/` root, discovers Markdown files through the active transport, and delegates each source to `ingest_source(...)`. The CLI only adds argument parsing, result dispatch, text output, and existing dataclass JSON serialization. Documentation records that R3.1 is local `.md` batch ingest only.

**Tech Stack:** Python 3.10+, standard library dataclasses/pathlib/json, pytest, existing filesystem and Obsidian CLI transport contracts.

## Global Constraints

- Do not modify `D:\ai\llmWiki\claude-obsidian`.
- Do not move or retag `v0.1.0-mvp`.
- Do not add runtime dependencies; `pyproject.toml` must keep `dependencies = []`.
- Do not add URL fetching, HTML cleaning, network access, BM25, vector search, reranking, or LLM synthesis.
- R3.1 supports local `.md` files only, matching the current `list_markdown(...)` transport contract.
- Use UTF-8 for Chinese text writes.
- Commit messages must be written in Chinese.

---

## File Structure

- Create: `llm_wiki_core/operations/ingest_batch.py`
  - Owns `BatchIngestItem`, `BatchIngestResult`, `ingest_batch(...)`, source-root validation, Markdown discovery, item aggregation, and batch status calculation.
- Modify: `llm_wiki_core/cli.py`
  - Adds `ingest-batch` parser, execution branch, and text output branch. Existing `_to_jsonable(...)` handles dataclass JSON.
- Create: `tests/unit/test_batch_ingest_operation.py`
  - Covers operation behavior, manifest effects, skip/force, validation, empty batches, deterministic ordering, and per-item failures.
- Create: `tests/unit/test_batch_ingest_cli.py`
  - Covers CLI text output, JSON output, error exit behavior, and failed-item text formatting.
- Create: `tests/unit/test_r3_batch_ingest_docs.py`
  - Guards public docs so R3.1 is described as local Markdown batch ingest only.
- Modify: `README.md`
  - Adds `ingest-batch` to quick start, command table, capabilities, and boundary language.
- Modify: `docs/user-guide.md`
  - Adds batch ingest usage after single-source ingest and removes "batch ingest outside MVP" wording.
- Modify: `docs/roadmap-schedule.md`
  - Records R3.1 Batch Ingest as complete inside R3 while keeping URL/retrieval/LLM work future.

---

### Task 1: Batch Ingest Operation

**Files:**
- Create: `tests/unit/test_batch_ingest_operation.py`
- Create: `llm_wiki_core/operations/ingest_batch.py`

**Interfaces:**
- Consumes:
  - `llm_wiki_core.operations.ingest.ingest_source(vault_root, source_path, force=False, transport=None) -> IngestResult`
  - `llm_wiki_core.operations.ingest._normalize_source_path(source_path) -> Path`
  - `llm_wiki_core.transport.runtime.select_runtime_transport(vault_root).transport`
  - Transport methods: `exists(relative_path)`, `list_markdown(root)`, `read_text(relative_path)`, `write_text(relative_path, content)`
- Produces:
  - `BatchIngestItem(source_path: str, status: str, files_created: list[str], files_updated: list[str], files_skipped: list[str], error_type: str | None, error_message: str | None)`
  - `BatchIngestResult(operation: str, status: str, root_path: str, total: int, succeeded: int, skipped: int, failed: int, items: list[BatchIngestItem], warnings: list[str], next_suggested_action: str)`
  - `ingest_batch(vault_root: str | Path, source_root: str | Path, force: bool = False, transport: object | None = None) -> BatchIngestResult`

- [ ] **Step 1: Write failing operation tests**

Create `tests/unit/test_batch_ingest_operation.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest


def _init_batch_vault(tmp_path: Path) -> None:
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Batch ingest test")


def _write_raw(vault: Path, relative: str, content: str) -> Path:
    source = vault / ".raw" / relative
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(content, encoding="utf-8")
    return source


def test_ingest_batch_ingests_multiple_markdown_sources_and_manifest_records(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    first = _write_raw(tmp_path, "articles/beta.md", "# Beta\n\nSecond source.")
    second = _write_raw(tmp_path, "articles/alpha.md", "# Alpha\n\nFirst source.")

    result = ingest_batch(tmp_path, ".raw/articles")

    assert result.operation == "ingest-batch"
    assert result.status == "success"
    assert result.root_path == ".raw/articles"
    assert result.total == 2
    assert result.succeeded == 2
    assert result.skipped == 0
    assert result.failed == 0
    assert [item.source_path for item in result.items] == [
        ".raw/articles/alpha.md",
        ".raw/articles/beta.md",
    ]
    assert first.read_text(encoding="utf-8") == "# Beta\n\nSecond source."
    assert second.read_text(encoding="utf-8") == "# Alpha\n\nFirst source."
    assert (tmp_path / "wiki" / "sources" / "Alpha.md").is_file()
    assert (tmp_path / "wiki" / "sources" / "Beta.md").is_file()

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert sorted(manifest["sources"]) == ["articles/alpha.md", "articles/beta.md"]


def test_ingest_batch_counts_unchanged_sources_as_skipped_and_force_reingests(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "articles/example.md", "# Example\n\nOriginal.")

    first = ingest_batch(tmp_path, ".raw/articles")
    assert first.status == "success"
    assert first.succeeded == 1

    source_page = tmp_path / "wiki" / "sources" / "Example.md"
    source_page.write_text("custom source page", encoding="utf-8")

    second = ingest_batch(tmp_path, ".raw/articles")
    assert second.status == "success"
    assert second.succeeded == 0
    assert second.skipped == 1
    assert second.items[0].status == "skipped"
    assert source_page.read_text(encoding="utf-8") == "custom source page"

    forced = ingest_batch(tmp_path, ".raw/articles", force=True)
    assert forced.status == "success"
    assert forced.succeeded == 1
    assert forced.skipped == 0
    assert "custom source page" not in source_page.read_text(encoding="utf-8")


def test_ingest_batch_rejects_missing_source_root(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)

    with pytest.raises(FileNotFoundError, match=r"Raw source root not found under \.raw/: \.raw/articles"):
        ingest_batch(tmp_path, ".raw/articles")


def test_ingest_batch_rejects_source_root_outside_raw(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)

    with pytest.raises(ValueError, match=r"source_root must be \.raw/ or under \.raw/"):
        ingest_batch(tmp_path, "notes")


def test_ingest_batch_rejects_raw_path_traversal(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)

    with pytest.raises(ValueError, match=r"source_root under \.raw/ must not contain '\.\.'"):
        ingest_batch(tmp_path, ".raw/../articles")


def test_ingest_batch_returns_empty_for_existing_root_without_markdown(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    notes = tmp_path / ".raw" / "notes"
    notes.mkdir(parents=True)
    (notes / "not-markdown.txt").write_text("plain text", encoding="utf-8")

    result = ingest_batch(tmp_path, ".raw/notes")

    assert result.status == "empty"
    assert result.total == 0
    assert result.succeeded == 0
    assert result.skipped == 0
    assert result.failed == 0
    assert result.items == []
    assert "Add Markdown files under .raw/" in result.next_suggested_action


def test_ingest_batch_accepts_single_markdown_file_root(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "articles/single.md", "# Single\n\nOnly one.")

    result = ingest_batch(tmp_path, ".raw/articles/single.md")

    assert result.status == "success"
    assert result.total == 1
    assert result.items[0].source_path == ".raw/articles/single.md"
    assert (tmp_path / "wiki" / "sources" / "Single.md").is_file()


def test_ingest_batch_captures_per_file_failure_and_continues(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    class PartialFailureTransport:
        def __init__(self) -> None:
            self.list_calls: list[str] = []
            self.files = {
                ".raw/.manifest.json": '{"schema_version": 1, "updated": "", "sources": {}}\n',
                ".raw/articles/ok.md": "# Ok\n\nReadable.",
                "wiki/index.md": "# Wiki Index\n\n## Sources\n",
                "wiki/log.md": "# Operation Log\n\n",
                "wiki/hot.md": "# Recent Context\n",
            }

        def exists(self, relative_path: str) -> bool:
            return relative_path in {".raw/articles", ".raw/articles/broken.md"} or relative_path in self.files

        def list_markdown(self, root: str) -> list[str]:
            self.list_calls.append(root)
            return [".raw/articles/broken.md", ".raw/articles/ok.md"]

        def read_text(self, relative_path: str) -> str:
            if relative_path == ".raw/articles/broken.md":
                raise ValueError("cannot read source")
            return self.files[relative_path]

        def write_text(self, relative_path: str, content: str) -> str:
            self.files[relative_path] = content
            return relative_path

    transport = PartialFailureTransport()

    result = ingest_batch(tmp_path, ".raw/articles", transport=transport)

    assert transport.list_calls == [".raw/articles"]
    assert result.status == "partial"
    assert result.total == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert [item.status for item in result.items] == ["failed", "success"]
    failed = result.items[0]
    assert failed.source_path == ".raw/articles/broken.md"
    assert failed.error_type == "ValueError"
    assert failed.error_message == "cannot read source"
    assert "wiki/sources/Ok.md" in transport.files
```

- [ ] **Step 2: Run operation tests to verify RED**

Run:

```powershell
python -m pytest tests/unit/test_batch_ingest_operation.py -q
```

Expected: FAIL during import with `ModuleNotFoundError: No module named 'llm_wiki_core.operations.ingest_batch'`.

- [ ] **Step 3: Implement the batch operation**

Create `llm_wiki_core/operations/ingest_batch.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_wiki_core.operations.ingest import IngestResult, _normalize_source_path, ingest_source
from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class BatchIngestItem:
    source_path: str
    status: str
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    error_type: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class BatchIngestResult:
    operation: str
    status: str
    root_path: str
    total: int
    succeeded: int
    skipped: int
    failed: int
    items: list[BatchIngestItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def ingest_batch(
    vault_root: str | Path,
    source_root: str | Path,
    force: bool = False,
    transport: object | None = None,
) -> BatchIngestResult:
    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    raw_root = _validate_raw_source_root(_normalize_source_path(source_root))

    if not active_transport.exists(raw_root):  # type: ignore[attr-defined]
        raise FileNotFoundError(f"Raw source root not found under .raw/: {raw_root}")

    source_paths = _discover_markdown(active_transport, raw_root)
    if not source_paths:
        return BatchIngestResult(
            operation="ingest-batch",
            status="empty",
            root_path=raw_root,
            total=0,
            succeeded=0,
            skipped=0,
            failed=0,
            next_suggested_action="Add Markdown files under .raw/ and run ingest-batch again.",
        )

    items: list[BatchIngestItem] = []
    for source_path in source_paths:
        try:
            result = ingest_source(root, source_path, force=force, transport=active_transport)
        except Exception as error:  # noqa: BLE001 - batch mode must record per-source failures.
            items.append(
                BatchIngestItem(
                    source_path=source_path,
                    status="failed",
                    error_type=type(error).__name__,
                    error_message=str(error),
                )
            )
            continue

        items.append(_item_from_ingest_result(result))

    succeeded = sum(1 for item in items if item.status == "success")
    skipped = sum(1 for item in items if item.status == "skipped")
    failed = sum(1 for item in items if item.status == "failed")

    return BatchIngestResult(
        operation="ingest-batch",
        status=_batch_status(succeeded=succeeded, skipped=skipped, failed=failed),
        root_path=raw_root,
        total=len(items),
        succeeded=succeeded,
        skipped=skipped,
        failed=failed,
        items=items,
        next_suggested_action="Query the wiki, lint the vault, or ingest another batch.",
    )


def _validate_raw_source_root(raw_relative: Path) -> str:
    raw_path = raw_relative.as_posix()
    parts = raw_relative.parts
    if not parts or parts[0] != ".raw":
        raise ValueError(f"source_root must be .raw/ or under .raw/: {raw_path}")
    if ".." in parts:
        raise ValueError(f"source_root under .raw/ must not contain '..': {raw_path}")
    return ".raw" if len(parts) == 1 else raw_path


def _discover_markdown(transport: object, raw_root: str) -> list[str]:
    if raw_root.lower().endswith(".md"):
        return [raw_root]
    return sorted(transport.list_markdown(raw_root))  # type: ignore[attr-defined]


def _item_from_ingest_result(result: IngestResult) -> BatchIngestItem:
    return BatchIngestItem(
        source_path=result.source_path,
        status=result.status,
        files_created=list(result.files_created),
        files_updated=list(result.files_updated),
        files_skipped=list(result.files_skipped),
    )


def _batch_status(succeeded: int, skipped: int, failed: int) -> str:
    if failed == 0:
        return "success"
    if succeeded or skipped:
        return "partial"
    return "failed"
```

- [ ] **Step 4: Run operation tests to verify GREEN**

Run:

```powershell
python -m pytest tests/unit/test_batch_ingest_operation.py -q
```

Expected: `8 passed`.

- [ ] **Step 5: Run focused existing ingest tests**

Run:

```powershell
python -m pytest tests/unit/test_ingest_operation.py tests/unit/test_batch_ingest_operation.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit Task 1**

Run:

```powershell
git add llm_wiki_core/operations/ingest_batch.py tests/unit/test_batch_ingest_operation.py
git commit -m "实现 R3.1 批量摄取核心操作"
```

---

### Task 2: CLI Entry Point And Output

**Files:**
- Create: `tests/unit/test_batch_ingest_cli.py`
- Modify: `llm_wiki_core/cli.py`

**Interfaces:**
- Consumes:
  - `ingest_batch(vault_root, source_root, force=False) -> BatchIngestResult`
  - `BatchIngestResult.items`
  - Existing CLI helpers: `_add_json_option(...)`, `_to_jsonable(...)`, `_print_error(...)`
- Produces:
  - CLI command: `llm-wiki ingest-batch <vault> <source-root> [--force] [--json]`
  - Human text summary for batch counts and failed items.
  - JSON output through the existing dataclass serializer.

- [ ] **Step 1: Write failing CLI tests**

Create `tests/unit/test_batch_ingest_cli.py` with:

```python
from __future__ import annotations

import json


def _last_json(stdout: str) -> dict[str, object]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    assert lines
    return json.loads(lines[-1])


def test_cli_ingest_batch_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI batch")
    articles = tmp_path / ".raw" / "articles"
    articles.mkdir(parents=True)
    (articles / "one.md").write_text("# One\n\nFirst.", encoding="utf-8")
    (articles / "two.md").write_text("# Two\n\nSecond.", encoding="utf-8")

    exit_code = main(["ingest-batch", str(tmp_path), ".raw/articles"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ingest-batch success" in output
    assert "root: .raw/articles" in output
    assert "total: 2" in output
    assert "succeeded: 2" in output
    assert "skipped: 0" in output
    assert "failed: 0" in output
    assert "next: Query the wiki, lint the vault, or ingest another batch." in output


def test_cli_ingest_batch_json_includes_items(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI batch JSON")
    articles = tmp_path / ".raw" / "articles"
    articles.mkdir(parents=True)
    (articles / "example.md").write_text("# Example\n\nJSON.", encoding="utf-8")

    exit_code = main(["ingest-batch", str(tmp_path), ".raw/articles", "--json"])

    assert exit_code == 0
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "ingest-batch"
    assert payload["status"] == "success"
    assert payload["root_path"] == ".raw/articles"
    assert payload["total"] == 1
    assert payload["succeeded"] == 1
    assert payload["failed"] == 0
    items = payload["items"]
    assert isinstance(items, list)
    assert items[0]["source_path"] == ".raw/articles/example.md"
    assert items[0]["status"] == "success"


def test_cli_ingest_batch_invalid_root_returns_error_exit_code(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI batch error")

    exit_code = main(["ingest-batch", str(tmp_path), "notes"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "ingest-batch error" in captured.err
    assert ".raw/" in captured.err


def test_cli_ingest_batch_prints_failed_items(monkeypatch, tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.ingest_batch import BatchIngestItem, BatchIngestResult

    def fake_ingest_batch(vault_root: str, source_root: str, force: bool = False) -> BatchIngestResult:
        return BatchIngestResult(
            operation="ingest-batch",
            status="partial",
            root_path=source_root,
            total=2,
            succeeded=1,
            skipped=0,
            failed=1,
            items=[
                BatchIngestItem(source_path=".raw/articles/ok.md", status="success"),
                BatchIngestItem(
                    source_path=".raw/articles/broken.md",
                    status="failed",
                    error_type="ValueError",
                    error_message="cannot read source",
                ),
            ],
            next_suggested_action="Query the wiki, lint the vault, or ingest another batch.",
        )

    monkeypatch.setattr("llm_wiki_core.cli.ingest_batch", fake_ingest_batch)

    exit_code = main(["ingest-batch", str(tmp_path), ".raw/articles"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ingest-batch partial" in output
    assert "failed items:" in output
    assert "- .raw/articles/broken.md: ValueError: cannot read source" in output
```

- [ ] **Step 2: Run CLI tests to verify RED**

Run:

```powershell
python -m pytest tests/unit/test_batch_ingest_cli.py -q
```

Expected: FAIL because `ingest-batch` is not yet a recognized command or `llm_wiki_core.cli.ingest_batch` is not defined.

- [ ] **Step 3: Modify imports in `llm_wiki_core/cli.py`**

Add this import near the existing operation imports:

```python
from llm_wiki_core.operations.ingest_batch import ingest_batch
```

- [ ] **Step 4: Add the parser branch**

In `build_parser()`, immediately after the existing `ingest` parser block, add:

```python
    ingest_batch_parser = subparsers.add_parser(
        "ingest-batch",
        help="Ingest Markdown raw sources under a .raw/ root.",
    )
    ingest_batch_parser.add_argument("vault", help="Path to the vault root.")
    ingest_batch_parser.add_argument("source_root", help="Vault-relative .raw/ root or Markdown file.")
    ingest_batch_parser.add_argument("--force", action="store_true", help="Re-ingest even when sources are unchanged.")
    _add_json_option(ingest_batch_parser)
```

- [ ] **Step 5: Add the execution branch**

In `_execute(args)`, immediately after the existing `ingest` branch, add:

```python
    if args.command == "ingest-batch":
        return ingest_batch(args.vault, args.source_root, force=args.force)
```

- [ ] **Step 6: Add text output**

In `_print_text_result(command, result)`, immediately after the existing `ingest` output branch, add:

```python
    if command == "ingest-batch":
        print(f"{result.operation} {result.status}")
        print(f"root: {result.root_path}")
        print(f"total: {result.total}")
        print(f"succeeded: {result.succeeded}")
        print(f"skipped: {result.skipped}")
        print(f"failed: {result.failed}")
        failed_items = [item for item in result.items if item.status == "failed"]
        if failed_items:
            print("failed items:")
            for item in failed_items:
                print(f"- {item.source_path}: {item.error_type}: {item.error_message}")
        print(f"next: {result.next_suggested_action}")
```

- [ ] **Step 7: Run CLI tests to verify GREEN**

Run:

```powershell
python -m pytest tests/unit/test_batch_ingest_cli.py -q
```

Expected: `4 passed`.

- [ ] **Step 8: Run focused CLI and JSON tests**

Run:

```powershell
python -m pytest tests/unit/test_batch_ingest_operation.py tests/unit/test_batch_ingest_cli.py tests/unit/test_cli_json_output.py tests/unit/test_mvp_smoke.py -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit Task 2**

Run:

```powershell
git add llm_wiki_core/cli.py tests/unit/test_batch_ingest_cli.py
git commit -m "接入 R3.1 批量摄取命令"
```

---

### Task 3: Public Documentation And Guard Tests

**Files:**
- Create: `tests/unit/test_r3_batch_ingest_docs.py`
- Modify: `README.md`
- Modify: `docs/user-guide.md`
- Modify: `docs/roadmap-schedule.md`

**Interfaces:**
- Consumes:
  - Public command contract from Task 2: `llm-wiki ingest-batch <vault> <source-root> [--force] [--json]`
  - R3.1 boundary: local `.md` files only under `.raw/`
- Produces:
  - Public docs that mention `ingest-batch`.
  - Public docs that keep URL ingest, HTML cleaning, deep retrieval, vector search, and LLM synthesis out of R3.1.
  - Guard tests that prevent later docs from claiming full R3 parity by accident.

- [ ] **Step 1: Write failing documentation guard tests**

Create `tests/unit/test_r3_batch_ingest_docs.py` with:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_documents_ingest_batch_command() -> None:
    readme = _read("README.md")

    assert "ingest-batch" in readme
    assert "llm-wiki ingest-batch <vault> .raw/articles" in readme
    assert "local Markdown" in readme or "本地 Markdown" in readme


def test_user_guide_documents_batch_ingest_and_keeps_future_boundaries() -> None:
    guide = _read("docs/user-guide.md")

    assert "llm-wiki ingest-batch <vault> .raw/articles" in guide
    assert "--force" in guide
    assert "--json" in guide
    assert "URL ingest" in guide
    assert "deep retrieval" in guide
    assert "outside R3.1" in guide
    assert "batch ingest, deep retrieval" not in guide


def test_roadmap_schedule_records_r3_1_batch_ingest_status() -> None:
    schedule = _read("docs/roadmap-schedule.md")

    assert "R3.1: Batch Ingest" in schedule
    assert "Status: complete." in schedule
    assert "local `.md` files under `.raw/`" in schedule
    assert "URL ingest" in schedule
    assert "future R3" in schedule
```

- [ ] **Step 2: Run documentation tests to verify RED**

Run:

```powershell
python -m pytest tests/unit/test_r3_batch_ingest_docs.py -q
```

Expected: FAIL because public docs do not yet document `ingest-batch`.

- [ ] **Step 3: Update `README.md`**

Make these content changes while preserving the existing README language style:

```markdown
Current version status: R3.1 adds local Markdown batch ingest on top of the MVP local loop. Full R3 work such as URL ingest, deep retrieval, vector search, and LLM synthesis remains future work.
```

Add `ingest-batch` to the capability list:

```markdown
- Batch ingest local `.md` files under `.raw/` while preserving raw sources and manifest traceability.
```

Add this quick-start command after the single-source ingest example:

```powershell
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-batch <vault> .raw/articles --force
```

Add this JSON example:

```powershell
llm-wiki ingest-batch <vault> .raw/articles --json
```

Add this command-table row:

```markdown
| `llm-wiki ingest-batch <vault> <source-root>` | Ingest local `.md` files under a `.raw/` root. |
```

Update current boundary language so it no longer lists batch ingest as missing. The boundary list should still say URL ingest, HTML cleanup, deep retrieval, vector search, LLM synthesis, and full `claude-obsidian` parity remain future work.

- [ ] **Step 4: Update `docs/user-guide.md`**

After the single-source ingest section, add:

```markdown
## Batch Ingest Raw Sources

R3.1 supports local Markdown batch ingest for `.md` files that already live under `.raw/`.

```powershell
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-batch <vault> .raw/articles --force
llm-wiki ingest-batch <vault> .raw/articles --json
```

Expected result:

- each discovered `.md` source is processed through the same ingest path as `llm-wiki ingest`;
- unchanged sources are counted as skipped unless `--force` is used;
- per-source failures are reported without blocking unrelated sources;
- raw files remain unchanged.

URL ingest, HTML cleanup, image ingest, deep retrieval, vector search, and LLM synthesis remain outside R3.1.
```

In "Machine-Readable CLI Output", add:

```powershell
llm-wiki ingest-batch <vault> .raw/articles --json
```

In "What Is Ready", add:

```markdown
- Local `.md` batch ingest under `.raw/`.
```

In "Current Boundaries", remove "batch ingest" from the unavailable list and keep the future boundaries:

```markdown
- URL ingest, HTML cleanup, image ingest, deep retrieval, vector search, LLM synthesis, and marketplace publishing are outside R3.1.
```

- [ ] **Step 5: Update `docs/roadmap-schedule.md`**

Inside the R3 section, add this subsection:

```markdown
### R3.1: Batch Ingest

Window: 2026-06-28

Status: complete.

Scope:

- Batch ingest local `.md` files under `.raw/`.
- Reuse the existing single-source ingest path.
- Preserve raw source files, manifest traceability, index/log/hot updates, and lint health.
- Report per-source success, skipped, and failed items.

Non-scope:

- URL ingest.
- HTML cleanup.
- Image ingest.
- Deep retrieval.
- BM25, vector search, hybrid retrieval, or reranking.
- LLM synthesis.

Follow-up:

- URL ingest and retrieval expansion remain future R3 work.
```

- [ ] **Step 6: Run documentation tests to verify GREEN**

Run:

```powershell
python -m pytest tests/unit/test_r3_batch_ingest_docs.py tests/unit/test_readme_hygiene.py tests/unit/test_release_docs.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Run full verification**

Run:

```powershell
python -m pytest -q
git diff --check
git -C D:\ai\llmWiki\claude-obsidian status --short --branch
git rev-parse v0.1.0-mvp^{}
```

Expected:

- pytest passes with the existing Windows shell dry-run skip if applicable.
- `git diff --check` has no output.
- `claude-obsidian` remains unchanged on its own branch.
- `v0.1.0-mvp^{}` still points to the pre-R3 MVP commit.

- [ ] **Step 8: Commit Task 3**

Run:

```powershell
git add README.md docs/user-guide.md docs/roadmap-schedule.md tests/unit/test_r3_batch_ingest_docs.py
git commit -m "补充 R3.1 批量摄取文档"
```

---

## Final Integration

- [ ] **Step 1: Run full suite one more time**

```powershell
python -m pytest -q
```

Expected: all tests pass, with the existing Windows-specific skip if still present.

- [ ] **Step 2: Inspect history and status**

```powershell
git log --oneline -6
git status --short --branch
```

Expected:

- The branch contains the design commit, plan commit, and three implementation commits.
- The working tree is clean.

- [ ] **Step 3: Update progress document**

Update `D:\ai\llmWiki\codex_doc\project_understanding_progress.md` with:

```markdown
## 阶段 76：R3.1 Batch Ingest 实施计划

状态：已完成

### 结果

- 新增实施计划：`D:\ai\llmWiki\llm-wiki-core\docs\superpowers\plans\2026-06-28-r3-1-batch-ingest.md`
- 计划提交：记录 `git commit` 返回的实际提交哈希和中文提交标题。
```

After implementation completes, append another stage that lists commits, tests, docs, branch status, tag status, and `claude-obsidian` status.

---

## Self-Review

- Spec coverage:
  - Batch operation, deterministic discovery, skip/force, missing root, outside `.raw/`, empty batch, partial failures, CLI text, CLI JSON, and docs are covered by Tasks 1-3.
  - Non-goals are enforced through docs wording and absence of dependencies/network code.
- Placeholder scan:
  - The plan contains concrete file paths, test commands, and code blocks rather than empty marker text.
- Type consistency:
  - `BatchIngestItem`, `BatchIngestResult`, and `ingest_batch(...)` names match between tests, operation, CLI, and docs.
  - CLI argument name is `source_root`; result field is `root_path`.
