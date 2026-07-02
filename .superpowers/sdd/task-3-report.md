# R4.0 Task 3 Report

## Scope

Task 3 implements adapter packaging documentation and guard tests for R4.0 without changing neutral core behavior.

## Modified Repository Files

- `docs/adapter-packaging-plan.md`
- `docs/capability-mapping.md`
- `docs/agent-behavioral-contract.md`
- `integrations/codex/README.md`
- `integrations/codex/skills/README.md`
- `integrations/codex/plugin/README.md`
- `integrations/codex/install/README.md`
- `tests/unit/test_codex_installer_smoke.py`
- `tests/unit/test_r4_0_adapter_packaging_docs.py`

## What Changed

### Guard Tests

- Added `tests/unit/test_r4_0_adapter_packaging_docs.py` to guard:
  - damaged text markers;
  - private local paths;
  - packaging plan sections and plugin decision wording;
  - capability mapping boundaries between core, Codex adapter, and Claude adapter;
  - behavioral contract wording for search and adapter parity;
  - Codex integration docs for repo-local mode, user-level skill mode, and plugin placeholder status.
- Extended `tests/unit/test_codex_installer_smoke.py` with a README portability assertion to prevent private path examples and platform-specific compatibility shell wording.

### Public Documentation

- Rewrote the adapter packaging plan as readable English documentation.
- Rewrote the capability mapping as a focused boundary table for R4.0.
- Rewrote the agent behavioral contract to document ingest, search, query, save, lint, parity, and forbidden behavior.
- Replaced Codex integration placeholder READMEs with adapter-facing documentation for:
  - repo-local mode;
  - user-level skill mode;
  - plugin future-target positioning;
  - portable installer usage.

## TDD Evidence

### RED

Command:

```powershell
python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py::test_install_readme_uses_portable_examples_not_private_paths -q
```

Result:

- `6 failed`
- Failures were caused by damaged text, missing required sections, placeholder READMEs, and private path examples.

### GREEN

Command:

```powershell
python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py -q
```

Result:

- `9 passed, 1 skipped`

## Verification

### Focused Verification

Command:

```powershell
python -m pytest tests/unit/test_readme_hygiene.py tests/unit/test_codex_adapter_assets.py tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py -q
```

Result:

- `18 passed, 1 skipped`

### Full Test Suite

Command:

```powershell
python -m pytest -q
```

Result:

- `200 passed, 6 failed, 1 skipped`

Out-of-scope failures:

- `tests/unit/test_completion_readiness_docs.py::test_readme_links_completion_docs`
- `tests/unit/test_r1_hardening_docs.py::test_readme_documents_machine_readable_cli_output`
- `tests/unit/test_r3_3_retrieval_docs.py::test_readme_documents_r3_3_search_command_and_boundaries`
- `tests/unit/test_r3_url_ingest_docs.py::test_readme_documents_url_ingest_and_boundaries`
- `tests/unit/test_release_docs.py::test_readme_links_release_readiness_docs`
- `tests/unit/test_release_process_docs.py::test_readme_links_release_process_docs`

These failures are tied to root `README.md` expectations and were not modified because Task 3 explicitly forbids editing the root `README.md`.

### Additional Checks

- `git diff --check`
  - No whitespace errors. Git reported LF/CRLF conversion warnings only.
- `Select-String -Path pyproject.toml -Pattern "dependencies = \[\]"`
  - Confirmed `dependencies = []`.

## Boundary Notes

- Karpathy gist remains the canonical abstract pattern.
- `AgriciDaniel/claude-obsidian` remains the Claude Code + Obsidian reference implementation.
- Codex packaging work in R4.0 is adapter-facing readiness for local Codex App / CLI usage.
- Plugin marketplace publication remains deferred.
