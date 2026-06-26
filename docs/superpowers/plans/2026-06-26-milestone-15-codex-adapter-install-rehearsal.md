# Milestone 15 Codex Adapter Install Rehearsal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the repo-local Codex adapter installer creates a Codex-discoverable, CLI-usable LLM Wiki vault.

**Architecture:** Keep adapter behavior thin. Add tests around generated `AGENTS.md` and command mapping docs, update the smallest source locations, then run a real PowerShell installer rehearsal on a temporary vault.

**Tech Stack:** Python 3.10+, pytest, PowerShell, Markdown, local filesystem transport.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not modify global Codex configuration.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Codex AGENTS Discovery Contract

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_init_operation.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/init.py`

**Interfaces:**
- Consumes: `init_vault(vault_root, purpose, adapter="codex")`
- Produces: generated `AGENTS.md` with MVP command list and natural language triggers

- [ ] **Step 1: Write failing test**

Add a test that initializes a vault and asserts `AGENTS.md` contains `llm-wiki status`, `llm-wiki continue`, `llm-wiki ingest`, `llm-wiki query`, `llm-wiki save`, `llm-wiki lint`, `set up wiki`, `check wiki status`, `resume wiki context`, and `artifact-level equivalence`.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_init_operation.py::test_init_writes_codex_agents_with_command_discovery -q`

Expected: failure because current generated `AGENTS.md` lacks the Codex command discovery block.

- [ ] **Step 3: Implement minimal AGENTS update**

Update `_agents_page()` in `llm_wiki_core/operations/init.py` to include the command list and natural language mapping already used by the Codex adapter assets.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_init_operation.py -q`

Expected: all init operation tests pass.

### Task 2: Codex Command Mapping Table Quality

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_codex_adapter_assets.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/COMMANDS.md`

**Interfaces:**
- Consumes: command mapping Markdown file
- Produces: valid Markdown table rows for command discovery docs

- [ ] **Step 1: Write failing table test**

Add a test that every non-separator row in the command mapping table starts with `|`, ends with `|`, and contains at least three pipe characters.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_codex_adapter_assets.py::test_codex_command_mapping_table_rows_are_well_formed -q`

Expected: failure because some rows are missing the trailing `|`.

- [ ] **Step 3: Fix table rows**

Add missing trailing pipes to the affected rows in `integrations/codex/COMMANDS.md`.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_codex_adapter_assets.py -q`

Expected: all Codex adapter asset tests pass.

### Task 3: Real PowerShell Installer Rehearsal

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/codex-adapter-install-rehearsal.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`

**Interfaces:**
- Consumes: `integrations/codex/install/install.ps1`
- Produces: documented installer-created vault evidence

- [ ] **Step 1: Run installer on temporary vault**

Run PowerShell installer with a temporary vault path and purpose.

- [ ] **Step 2: Verify generated vault**

Run `llm-wiki status`, `llm-wiki continue`, and `llm-wiki lint` against the installer-created vault. Inspect generated `AGENTS.md` for Codex command discovery text.

- [ ] **Step 3: Record rehearsal**

Create `docs/codex-adapter-install-rehearsal.md` with command evidence, generated vault checks, lint result, and cleanup notes.

- [ ] **Step 4: Update README**

Move current status to Milestone 15 and link the Codex adapter install rehearsal.

### Task 4: Progress And Final Verification

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: all Milestone 15 results
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

