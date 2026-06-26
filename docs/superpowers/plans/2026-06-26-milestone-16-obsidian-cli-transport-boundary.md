# Milestone 16 Obsidian CLI Transport Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent detected but unimplemented Obsidian CLI from being treated as the preferred runtime transport.

**Architecture:** Keep filesystem as the only implemented runtime transport. Extend transport snapshot metadata with implementation state and add an Obsidian CLI placeholder class that raises a clear contract-boundary error.

**Tech Stack:** Python 3.10+, pytest, PowerShell, Markdown.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Do not implement actual Obsidian CLI read/write/search in this milestone.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Snapshot Implementation State

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_transport_detection.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/detect_transport.py`

**Interfaces:**
- Consumes: `detect_transport(vault_root, force=False)`
- Produces: `TransportAvailability(available, executable, implemented, reason)`

- [ ] **Step 1: Write failing tests**

Update transport detection tests so detected Obsidian CLI is recorded as available but not implemented, while preferred remains filesystem.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_transport_detection.py -q`

Expected: failure because current code still prefers `obsidian-cli` and lacks `implemented`.

- [ ] **Step 3: Implement snapshot metadata**

Add `implemented` and `reason` to `TransportAvailability`, serialize them to JSON, and set:

- `obsidian-cli`: `implemented=False`
- `filesystem`: `implemented=True`
- fresh `preferred`: `filesystem`

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_transport_detection.py -q`

Expected: all transport detection tests pass.

### Task 2: Obsidian CLI Transport Placeholder

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/obsidian_cli.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_obsidian_cli_transport.py`

**Interfaces:**
- Produces: `ObsidianCliTransport`
- Produces: `ObsidianCliTransportNotImplementedError`

- [ ] **Step 1: Write failing tests**

Test that `ObsidianCliTransport` exposes `read_text`, `write_text`, `append_text`, `exists`, `list_markdown`, and `search_text`, and that each raises `ObsidianCliTransportNotImplementedError`.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_obsidian_cli_transport.py -q`

Expected: import failure because placeholder module does not exist.

- [ ] **Step 3: Implement placeholder**

Create a class with the expected methods. Each method raises the same clear boundary error: actual Obsidian CLI transport is not implemented in the MVP.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_obsidian_cli_transport.py -q`

Expected: all placeholder tests pass.

### Task 3: Docs And Rehearsal

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/obsidian-cli-transport-boundary-rehearsal.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/transport-contract.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`

**Interfaces:**
- Consumes: updated detection and placeholder behavior
- Produces: documented boundary and local rehearsal evidence

- [ ] **Step 1: Run boundary rehearsal**

Run `llm-wiki init`, `llm-wiki detect-transport --force`, `llm-wiki status`, and inspect `.vault-meta/transport.json` in a temporary vault.

- [ ] **Step 2: Record rehearsal**

Document that filesystem is preferred and Obsidian CLI, if detected, is only a contract boundary with `implemented: false`.

- [ ] **Step 3: Update README and contract docs**

Move current status to Milestone 16 and clarify detection vs implementation.

### Task 4: Progress And Final Verification

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: all Milestone 16 changes
- Produces: user-facing progress update and verification evidence

- [ ] **Step 1: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

- [ ] **Step 2: Run full tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

Expected: all tests pass, with the known Windows POSIX shell dry-run skip.

- [ ] **Step 3: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 4: Verify generated artifacts are cleaned**

Check no `__pycache__`, `*.egg-info`, `build`, or temporary rehearsal vault remains after cleanup.

