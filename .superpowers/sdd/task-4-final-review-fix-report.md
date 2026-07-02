# Task 4 Final Review Fix Report

## 2026-07-02 R4.0 final review fix

- Scope:
  - Fix public Codex command contract coverage for `ingest-batch` and `ingest-url`.
  - Strengthen public adapter packaging doc guards for damaged text and private paths.
- TDD evidence:
  - RED: `python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py -q`
    - failed because `docs/codex-command-contract.md` did not include the `ingest-batch` mapping asserted by the focused test.
  - GREEN: `python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_r3_3_retrieval_docs.py -q`
    - result: `13 passed`
- Files changed:
  - `docs/codex-command-contract.md`
  - `tests/unit/test_r4_0_adapter_packaging_docs.py`
  - `tests/unit/test_r3_3_retrieval_docs.py`
- Final behavior/documentation outcome:
  - Public Codex command contract now states that natural-language triggers are required and slash commands are target UX.
  - `ingest` is explicitly scoped to one local Markdown source under `.raw/`.
  - `ingest-batch` is documented as local Markdown folder/root ingest under `.raw/`, including per-source wiki artifact updates plus manifest/index/log/hot updates.
  - `ingest-url` is documented as one explicit URL ingest that preserves an immutable `.raw/url/` snapshot before wiki artifact generation, without claiming crawling, readability, JavaScript rendering, or authenticated fetch support.
  - `search` remains documented as read-only ranked durable wiki page retrieval before synthesis.
  - Public adapter doc guards now include `docs/codex-command-contract.md` and broader mojibake/private-path coverage.
