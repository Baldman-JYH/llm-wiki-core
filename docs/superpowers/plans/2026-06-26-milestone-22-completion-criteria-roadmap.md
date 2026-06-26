# Milestone 22 Completion Criteria / Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add completion criteria and a roadmap, then reconcile stale early planning docs with the implemented transport boundary.

**Architecture:** Documentation-only milestone with static tests. No runtime behavior changes.

**Tech Stack:** Markdown, pytest static checks.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Verify artifact-level equivalence, not byte-for-byte LLM-authored prose.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Completion Static Tests

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_completion_readiness_docs.py`

**Interfaces:**
- Consumes: completion docs, roadmap, README, early planning docs
- Produces: regression coverage for completion boundary and transport wording

- [ ] **Step 1: Add failing tests**

Assert:

- completion criteria and roadmap exist;
- README links them;
- early planning docs no longer claim Obsidian CLI is runtime preferred before implementation.

- [ ] **Step 2: Verify red**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/unit/test_completion_readiness_docs.py -q`

Expected: fail before docs and wording updates.

### Task 2: Completion Docs

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/completion-criteria.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/roadmap.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/mvp-scope.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/capability-mapping.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/milestone-plan.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/release-readiness-checklist.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`

**Interfaces:**
- Consumes: Milestone 1-21 results
- Produces: completion boundary and future roadmap

- [ ] **Step 1: Add completion criteria**

Define "MVP Local Complete" and separate it from full parity.

- [ ] **Step 2: Add roadmap**

Group future work into transport, ingest/retrieval, adapters, packaging, and advanced knowledge organization.

- [ ] **Step 3: Reconcile stale transport docs**

Replace old Obsidian CLI preferred-runtime wording with the implemented boundary: detection is available, actual read/write/search is not implemented, filesystem remains runtime.

### Task 3: Verification And Progress

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: test and doc results
- Produces: user-facing progress update

- [ ] **Step 1: Run focused tests**

Run completion doc tests.

- [ ] **Step 2: Run full tests**

Run all pytest tests.

- [ ] **Step 3: Verify reference repo and generated artifacts**

Check `claude-obsidian` status and generated artifact scan.

- [ ] **Step 4: Update progress doc**

Append Milestone 22 result under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.
