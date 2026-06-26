# Milestone 13 Installer Smoke Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe dry-run smoke tests for Codex adapter installer scripts.

**Architecture:** Keep installers as thin wrappers. Add dry-run switches that print command plans without executing them. Tests validate script contents and execute dry-run mode only when the local shell executable is available.

**Tech Stack:** PowerShell, POSIX shell, Python 3.10+, pytest.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits because `D:/ai/llmWiki/llm-wiki-core` is not currently a Git repository.

---

### Task 1: Installer Smoke Tests

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_codex_installer_smoke.py`

**Interfaces:**
- Consumes: existing installer scripts
- Produces: failing tests for dry-run support and status/continue hints

- [ ] **Step 1: Write failing tests**

Add tests for PowerShell and shell dry-run support. Static checks must always run. Subprocess dry-run checks should skip if the relevant shell executable is missing.

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest tests\unit\test_codex_installer_smoke.py -q`

Expected: failures because dry-run support does not exist.

### Task 2: Installer Dry-Run Support

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/install/install.ps1`
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/install/install.sh`
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/install/README.md`

**Interfaces:**
- Consumes: tests from Task 1
- Produces:
  - `install.ps1 -DryRun`
  - `install.sh --dry-run <vault-path> <purpose>`
  - status/continue next-step hints

- [ ] **Step 1: Add PowerShell dry-run**

Implement `-DryRun`, print planned commands, and skip execution.

- [ ] **Step 2: Add shell dry-run**

Implement `--dry-run`, print planned commands, and skip execution.

- [ ] **Step 3: Run focused tests**

Run: `python -m pytest tests\unit\test_codex_installer_smoke.py tests\unit\test_codex_adapter_assets.py -q`

Expected: tests pass.

### Task 3: Docs And Progress

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: implemented dry-run support
- Produces: documented Milestone 13 state

- [ ] **Step 1: Update README**

Add Milestone 13 spec/plan references and installer dry-run examples.

- [ ] **Step 2: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 13 changes
- Produces: final verification evidence

- [ ] **Step 1: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 2: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 3: Verify no Python cache directories remain**

Run: `Get-ChildItem -Path 'D:\ai\llmWiki\llm-wiki-core' -Recurse -Directory -Filter '__pycache__'`

Expected: no output after cleanup if cleanup is needed.

