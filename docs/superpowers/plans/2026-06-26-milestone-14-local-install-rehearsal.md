# Milestone 14 Local Install Rehearsal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the installed `llm-wiki` console entrypoint can run the MVP loop on a temporary local vault.

**Architecture:** No production code changes are expected. Treat this as a local verification pass plus documentation update.

**Tech Stack:** PowerShell, Python 3.10+, pytest, local filesystem transport.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Keep the rehearsal Windows-native and do not rely on WSL or Git Bash.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless the user explicitly asks.

---

### Task 1: Capture Preflight State

**Files:**
- Read-only inspection under `D:/ai/llmWiki/llm-wiki-core`

**Interfaces:**
- Consumes: current working tree and generated-artifact baseline
- Produces: knowledge of whether install-generated files already existed

- [ ] **Step 1: Check install-generated metadata baseline**

Inspect `*.egg-info`, `build`, and existing temporary rehearsal folders before running editable install.

### Task 2: Run Real CLI Rehearsal

**Files:**
- Temporary vault outside committed source, or a cleaned temporary folder

**Interfaces:**
- Consumes: installed `llm-wiki` console entrypoint
- Produces: command output proving the MVP loop works

- [ ] **Step 1: Install package in editable mode**

Run: `python -m pip install -e .`

- [ ] **Step 2: Run installed command loop**

Run:

```powershell
llm-wiki --version
llm-wiki init <vault> --purpose "Milestone 14 local install rehearsal"
llm-wiki detect-transport <vault> --force
llm-wiki status <vault>
llm-wiki continue <vault>
llm-wiki ingest <vault> .raw\articles\rehearsal.md
llm-wiki query <vault> "rehearsal wiki"
llm-wiki save <vault> --title "Rehearsal Insight" --content "..."
llm-wiki lint <vault>
```

### Task 3: Record Evidence

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/local-install-rehearsal.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: rehearsal command results
- Produces: documented Milestone 14 evidence

- [ ] **Step 1: Write rehearsal report**

Record commands, outcome, vault handling, transport result, and any generated metadata cleanup.

- [ ] **Step 2: Update project README**

Move current status to Milestone 14 and link the rehearsal report.

- [ ] **Step 3: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 14 documentation and local install side effects
- Produces: final verification evidence

- [ ] **Step 1: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

- [ ] **Step 2: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 3: Verify no unexpected Python cache directories remain**

Run: `Get-ChildItem -Path 'D:\ai\llmWiki\llm-wiki-core' -Recurse -Directory -Filter '__pycache__'`

Expected: no output after cleanup if cleanup is needed.

