# R4.0 Final Review Fix Progress

## Phase 1 - Scope and Design

- Date: 2026-07-02
- Scope confirmed from final review:
  - Update `docs/codex-command-contract.md` so the public Codex command contract matches current R4.0 command coverage for `ingest`, `ingest-batch`, `ingest-url`, and `search`.
  - Strengthen `tests/unit/test_r4_0_adapter_packaging_docs.py` damaged-text and private-path guard coverage, including `docs/codex-command-contract.md`.
- Constraints confirmed:
  - Keep the command contract in public English documentation style.
  - Do not add local absolute paths.
  - Do not claim deferred capabilities are implemented.
  - Do not touch neutral core runtime or unrelated docs.
- TDD plan:
  - First tighten focused tests so they fail on the current gaps.
  - Then minimally update the contract doc and guard expectations until focused tests pass.

## Phase 2 - RED Verification

- Updated focused adapter packaging doc tests to:
  - include `docs/codex-command-contract.md` in the public doc hygiene guard,
  - broaden mojibake marker coverage,
  - assert public Codex contract coverage for `ingest-batch` and `ingest-url`.
- Ran:
  - `python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py -q`
- Result:
  - RED confirmed.
  - Current failure shows `docs/codex-command-contract.md` is missing the `ingest-batch` mapping required by the new assertions.

## Phase 3 - GREEN Verification

- Updated `docs/codex-command-contract.md` to:
  - declare natural-language triggers as required and slash commands as target UX,
  - add command mapping rows for `ingest-batch` and `ingest-url`,
  - clarify `ingest` as one local Markdown source under `.raw/`,
  - define `ingest-batch` as local Markdown folder/root ingest under `.raw/`,
  - define `ingest-url` as one explicit URL that writes immutable `.raw/url/` snapshots before wiki artifacts,
  - keep `search` read-only over durable wiki pages before synthesis,
  - keep deferred capabilities unclaimed.
- Updated focused tests to match the durable-page wording for public search semantics.
- Ran:
  - `python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_r3_3_retrieval_docs.py -q`
- Result:
  - GREEN, `13 passed`.

## Phase 4 - Reporting and Commit Prep

- Appended the full fix report to:
  - `.superpowers/sdd/task-4-final-review-fix-report.md`
- Ready to commit the scoped documentation and test updates with a Chinese commit message.
