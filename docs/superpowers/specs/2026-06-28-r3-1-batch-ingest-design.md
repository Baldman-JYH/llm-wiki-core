# R3.1 Batch Ingest Design

Date: 2026-06-28

## Goal

Add a conservative batch ingest workflow for local Markdown raw sources.

R3.1 should let users ingest many `.raw/` Markdown files in one command while preserving the current LLM Wiki guarantees: raw sources remain unchanged, generated pages stay traceable to source paths, manifest records remain accurate, and lint health remains testable.

## Background

The current ingest path is single-source:

- `ingest_source(vault_root, source_path, force=False, transport=None)`
- source path must be under `.raw/`;
- the source page is written under `wiki/sources/`;
- `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, and `.raw/.manifest.json` are updated;
- unchanged sources are skipped unless `force=True`.

R3 includes URL ingest, batch ingest, deep retrieval, BM25/vector search, and LLM synthesis policy. These are separate concerns. Batch ingest is the safest first R3 slice because it reuses the existing local source contract and does not add network access or dependencies.

## Design Summary

R3.1 adds a batch operation that discovers Markdown files under a `.raw/` path and calls `ingest_source()` for each file.

The batch layer should coordinate iteration, reporting, and partial failures. It should not duplicate the single-source ingest logic.

## User-Facing Behavior

CLI:

```powershell
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-batch <vault> .raw/articles --force
llm-wiki ingest-batch <vault> .raw/articles --json
```

Default behavior:

- recursively discovers Markdown files under the supplied `.raw/` directory;
- supports `.md` files in R3.1, matching the current transport contract;
- processes files in deterministic sorted order;
- skips unchanged files by reusing `ingest_source(..., force=False)`;
- continues after per-file failures and reports them;
- returns a non-error command exit if the batch command itself was valid, even when individual sources fail;
- uses JSON output to expose per-source success, skipped, and failed entries for automation.

## Operation API

Create a new operation module:

- `llm_wiki_core/operations/ingest_batch.py`

Proposed dataclasses:

```python
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
```

Function:

```python
def ingest_batch(
    vault_root: str | Path,
    source_root: str | Path,
    force: bool = False,
    transport: object | None = None,
) -> BatchIngestResult:
    ...
```

`source_root` follows the same safety model as single-source ingest:

- it must resolve to `.raw/` or a descendant of `.raw/`;
- it must not contain `..`;
- an absolute path is accepted only when it contains `.raw` and can be normalized to a vault-relative `.raw/...` path;
- a missing source root raises `FileNotFoundError`;
- a source root that points to a file should batch a single file if it is Markdown.

## Discovery Rules

Batch discovery should use the active transport rather than direct filesystem reads wherever practical.

For the MVP-sized R3.1, the operation may use the selected transport's `list_markdown(root)` method to discover Markdown files. This preserves compatibility with both filesystem and verified Obsidian CLI transports. Extending discovery to `.markdown` can be handled later as a transport contract change.

Expected roots:

- `.raw/`
- `.raw/articles`
- `.raw/notes`
- `.raw/articles/example.md`

If `source_root` is a Markdown file, process that one file.

If no Markdown files are found, return:

- `status: "empty"`
- `total: 0`
- no item failures
- `next_suggested_action` explaining to add Markdown files under `.raw/`.

## Status Semantics

Batch-level status:

- `success`: at least one item succeeded or skipped, and none failed;
- `partial`: at least one item failed and at least one item succeeded or skipped;
- `failed`: all discovered items failed;
- `empty`: no Markdown files were discovered.

Item status:

- `success`: `ingest_source()` returned success;
- `skipped`: `ingest_source()` returned skipped;
- `failed`: `ingest_source()` raised an exception for that item.

The batch command should continue after item failures so one bad raw source does not block unrelated sources.

## CLI Text Output

Human-readable output should be compact:

```text
ingest-batch success
root: .raw/articles
total: 3
succeeded: 2
skipped: 1
failed: 0
next: Query the wiki, lint the vault, or ingest another batch.
```

If failures exist:

```text
failed items:
- .raw/articles/broken.md: ValueError: source_path must be under .raw/
```

JSON output should use the existing `_to_jsonable()` path and include `items`.

## Documentation

Update public docs:

- `README.md`
- `docs/user-guide.md`
- `docs/roadmap-schedule.md`

The docs should state that R3.1 supports local Markdown batch ingest only. URL ingest, HTML cleanup, image ingest, BM25/vector search, and LLM synthesis remain future R3 work.

## Tests

New test file:

- `tests/unit/test_batch_ingest_operation.py`

Test coverage:

- batch ingests multiple Markdown files under `.raw/` and updates manifest records;
- batch processes files in deterministic order;
- unchanged files are counted as skipped;
- `--force` re-ingests unchanged sources;
- missing source root raises a clear error;
- source root outside `.raw/` is rejected;
- no Markdown files returns `status == "empty"`;
- per-file failures are captured as failed items while other files continue;
- CLI text output prints summary counts;
- CLI JSON output contains per-item records;
- transport-backed discovery and ingest are used where tests can reasonably spy on transport calls.

Existing tests for single-source ingest should remain unchanged.

## Non-Goals

- No URL fetching.
- No HTML cleaning.
- No network access.
- No new runtime dependencies.
- No BM25, vector search, hybrid retrieval, reranking, or LLM synthesis.
- No changes to Obsidian CLI transport behavior.
- No changes to `claude-obsidian`.
- No tag movement.

## Acceptance Criteria

- `llm-wiki ingest-batch <vault> .raw/...` works for local Markdown files.
- Raw sources are not modified.
- Each ingested source has a manifest record.
- Index, log, and hot cache continue to update through the existing single-source ingest behavior.
- Partial failures are represented in the result object and JSON output.
- Focused batch ingest tests pass.
- Full test suite passes.
- Documentation clearly says R3.1 is local Markdown batch ingest only.
