# R4.2 Adapter Parity Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish and test the first Codex / Claude adapter parity baseline without implementing Claude-specific runtime assets.

**Architecture:** Keep `llm-wiki-core` as the neutral owner of durable Markdown Wiki artifacts and operations. Add public docs and guard tests that classify Codex surfaces, future Claude surfaces, and deferred `claude-obsidian` capabilities against the same artifact-level parity contract. No neutral core Python behavior changes are included.

**Tech Stack:** Markdown docs, Python standard library tests with `pytest`, existing adapter docs under `integrations/codex/` and `integrations/claude/`.

## Global Constraints

- R4.2 must not add runtime dependencies; `pyproject.toml` must keep `dependencies = []`.
- R4.2 must not change neutral core operation behavior.
- R4.2 must not implement `.claude-plugin` generation.
- R4.2 must not implement Claude Code hooks.
- R4.2 must not implement Claude Code subagents.
- R4.2 must not implement marketplace-grade Codex plugin packaging.
- R4.2 must not implement `autoresearch`, canvas, hybrid retrieval, DragonScale, methodology modes, automatic Git commits, or remote Codex Web support.
- R4.2 must use artifact-level parity, not byte-for-byte parity.
- Public docs must identify Karpathy's LLM Wiki gist as the canonical abstract pattern.
- Public docs must identify `AgriciDaniel/claude-obsidian` as a Claude Code + Obsidian reference implementation case.
- Docs and tests must avoid private local absolute paths.
- Commit messages must be written in Chinese.

---

## File Structure

- Create `docs/adapter-parity-baseline.md`: public parity contract that explains canonical sources, artifact-level parity, layer boundaries, command intent mapping, and deferred capabilities.
- Modify `integrations/claude/README.md`: replace the placeholder with a reconstruction boundary and command mapping for future Claude Code support.
- Modify `docs/capability-mapping.md`: add Claude adapter behavior, artifact-level parity language, and deferred advanced `claude-obsidian` capabilities.
- Modify `docs/roadmap.md`: record that R4.2 adapter parity baseline is complete after implementation.
- Modify `docs/roadmap-schedule.md`: add an R4.2 schedule entry.
- Create `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`: guard the new docs against overclaiming full `claude-obsidian` parity, leaking adapter behavior into core, private paths, and missing command mapping.
- Modify external `../codex_doc/project_understanding_progress.md`: record implementation progress outside the repository.
- Do not modify neutral core operation files under `src/llm_wiki/`.

---

### Task 1: Public Adapter Parity Baseline Document

**Files:**
- Create: `docs/adapter-parity-baseline.md`
- Create: `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`

**Interfaces:**
- Consumes: R4.2 spec at `docs/superpowers/specs/2026-07-02-r4-2-adapter-parity-baseline-design.md`
- Produces: public parity doc and initial guard tests for canonical sources, parity definition, command intent mapping, and deferred features

- [ ] **Step 1: Write failing public parity doc tests**

Create `tests/unit/test_r4_2_adapter_parity_baseline_docs.py` with this content:

```python
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_adapter_parity_baseline_doc_exists_and_is_public() -> None:
    text = _read("docs/adapter-parity-baseline.md")

    assert "# Adapter Parity Baseline" in text
    assert "Karpathy's LLM Wiki gist is the canonical abstract pattern." in text
    assert "`AgriciDaniel/claude-obsidian` is a reference implementation case" in text
    assert "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f" in text
    assert "https://github.com/AgriciDaniel/claude-obsidian" in text


def test_adapter_parity_baseline_defines_artifact_level_parity() -> None:
    text = _read("docs/adapter-parity-baseline.md")

    assert "## Parity Definition" in text
    assert "Artifact-level parity is required." in text
    assert "Byte-for-byte parity is not required." in text
    assert "same vault structure" in text
    assert "same raw-source immutability rule" in text
    assert "compatible frontmatter and wikilinks" in text
    assert "updated `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`" in text
    assert "equivalent lint and health checks" in text


def test_adapter_parity_baseline_maps_codex_and_claude_to_neutral_commands() -> None:
    text = _read("docs/adapter-parity-baseline.md")

    expected_rows = [
        "| Set up a wiki | `set up wiki` | `/wiki` | `llm-wiki init <vault> --purpose \"...\"` |",
        "| Check transport | `check transport` | `/wiki transport` | `llm-wiki detect-transport <vault>` |",
        "| Check status | `check wiki status` | `/wiki status` | `llm-wiki status <vault>` |",
        "| Continue context | `continue wiki` | `/wiki` on existing vault | `llm-wiki continue <vault>` |",
        "| Ingest one source | `ingest this source` | `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |",
        "| Ingest a folder | `ingest this folder` | `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |",
        "| Ingest a URL | `ingest this URL` | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |",
        "| Search pages | `search wiki for X` | `/wiki search X` | `llm-wiki search <vault> \"X\"` |",
        "| Ask a question | `what does the wiki know about X` | `/wiki query X` | `llm-wiki query <vault> \"X\"` |",
        "| Save insight | `save this insight` | `/save` | `llm-wiki save <vault> --title \"...\" --content \"...\"` |",
        "| Lint health | `lint the wiki` | `/wiki lint` | `llm-wiki lint <vault>` |",
    ]

    for row in expected_rows:
        assert row in text


def test_adapter_parity_baseline_defers_advanced_claude_obsidian_features() -> None:
    text = _read("docs/adapter-parity-baseline.md")

    deferred = [
        "`autoresearch`",
        "canvas workflows",
        "hybrid retrieval and reranking",
        "DragonScale or log-folding memory",
        "methodology modes",
        "Claude Code hooks",
        "Claude Code subagents",
        "marketplace-grade Codex plugin packaging",
    ]
    for item in deferred:
        assert item in text

    forbidden_claims = [
        "full claude-obsidian parity is complete",
        "byte-for-byte parity is required",
        "Claude hooks are neutral core",
        "Claude subagents are neutral core",
        "marketplace-grade Codex plugin is complete",
    ]
    lower_text = text.lower()
    for claim in forbidden_claims:
        assert claim not in lower_text


def test_r4_2_public_parity_doc_has_no_private_paths_or_damaged_text() -> None:
    text = _read("docs/adapter-parity-baseline.md")
    damaged = ["\ufffd", "闁", "娑", "閻", "闂", "濡ょ姴鐭侀惁"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\"]

    assert not [marker for marker in damaged if marker in text]
    for pattern in private_path_patterns:
        assert not re.search(pattern, text), f"docs/adapter-parity-baseline.md contains {pattern}"
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py -q
```

Expected: fail because `docs/adapter-parity-baseline.md` does not exist.

- [ ] **Step 3: Create the public parity baseline document**

Create `docs/adapter-parity-baseline.md` with this content:

```markdown
# Adapter Parity Baseline

Date: 2026-07-02

## Positioning

Karpathy's LLM Wiki gist is the canonical abstract pattern.

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

`AgriciDaniel/claude-obsidian` is a reference implementation case for Claude Code + Obsidian.

https://github.com/AgriciDaniel/claude-obsidian

`llm-wiki-core` is the neutral implementation layer for local durable Markdown Wiki artifacts. It should absorb the reusable LLM Wiki rules while keeping agent-specific command surfaces in adapters.

## Parity Definition

Artifact-level parity is required.

Byte-for-byte parity is not required.

Codex App, Codex CLI, and a future Claude Code adapter should be considered equivalent when they produce compatible durable outcomes:

- same vault structure;
- same raw-source immutability rule;
- same page categories;
- compatible frontmatter and wikilinks;
- updated `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`;
- equivalent operation logs;
- equivalent lint and health checks;
- equivalent command intent mapping.

The project must not claim full `claude-obsidian` feature parity until those features are implemented and verified in their own milestones.

## Layer Boundaries

### Neutral Core

The neutral core owns durable artifacts and portable operations:

- `init`
- `detect-transport`
- `status`
- `continue`
- `ingest`
- `ingest-batch`
- `ingest-url`
- `search`
- `query`
- `save`
- `lint`

The core owns file formats, raw-source preservation, frontmatter policy, wikilink policy, transport contracts, index maintenance, log maintenance, hot context maintenance, and lint health.

### Codex Adapter

The Codex adapter owns local Codex App and Codex CLI usage:

- Codex skill instructions;
- natural-language trigger mapping;
- `AGENTS.md` template guidance;
- repo-local installation guidance;
- explicit user-level skill installation;
- future optional Codex plugin packaging.

The Codex adapter maps user intent to neutral core commands. It does not reimplement core behavior.

### Claude Adapter

The future Claude adapter should own Claude Code-specific behavior:

- `CLAUDE.md` or equivalent schema guidance;
- slash commands such as `/wiki` and `/save`;
- hook configuration;
- subagent descriptions;
- Claude-specific installation packaging.

Claude Code hooks and subagents are adapter-only behavior. They are not neutral core behavior.

## Command Intent Mapping

| Intent | Codex surface | Claude surface | Neutral command |
|---|---|---|---|
| Set up a wiki | `set up wiki` | `/wiki` | `llm-wiki init <vault> --purpose "..."` |
| Check transport | `check transport` | `/wiki transport` | `llm-wiki detect-transport <vault>` |
| Check status | `check wiki status` | `/wiki status` | `llm-wiki status <vault>` |
| Continue context | `continue wiki` | `/wiki` on existing vault | `llm-wiki continue <vault>` |
| Ingest one source | `ingest this source` | `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |
| Ingest a folder | `ingest this folder` | `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |
| Ingest a URL | `ingest this URL` | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |
| Search pages | `search wiki for X` | `/wiki search X` | `llm-wiki search <vault> "X"` |
| Ask a question | `what does the wiki know about X` | `/wiki query X` | `llm-wiki query <vault> "X"` |
| Save insight | `save this insight` | `/save` | `llm-wiki save <vault> --title "..." --content "..."` |
| Lint health | `lint the wiki` | `/wiki lint` | `llm-wiki lint <vault>` |

## Deferred Capabilities

The following capabilities from the `claude-obsidian` reference remain deferred until separate designs approve them:

- `autoresearch`;
- canvas workflows;
- hybrid retrieval and reranking;
- DragonScale or log-folding memory;
- methodology modes such as LYT, PARA, and Zettelkasten;
- multi-agent batch orchestration;
- Obsidian-specific dashboards, bases, plugins, and advanced templates;
- Claude Code hooks that mutate local state;
- Claude Code subagents;
- marketplace-grade Codex plugin packaging;
- automatic Git commits.

## Verification Rule

R4.2 is a documentation and guard-test milestone. It should require no live Claude Code, Obsidian, or Codex App process.
```

- [ ] **Step 4: Run the focused tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py -q
```

Expected: `5 passed`.

- [ ] **Step 5: Commit Task 1**

Run:

```powershell
git add docs/adapter-parity-baseline.md tests/unit/test_r4_2_adapter_parity_baseline_docs.py
git commit -m "补充 R4.2 适配器等效基线文档"
```

---

### Task 2: Claude Adapter Reconstruction Boundary

**Files:**
- Modify: `integrations/claude/README.md`
- Modify: `docs/capability-mapping.md`
- Modify: `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`

**Interfaces:**
- Consumes: public parity definition from Task 1
- Produces: Claude adapter reconstruction boundary and capability mapping that later implementation can follow

- [ ] **Step 1: Add failing Claude boundary and capability mapping tests**

Append this content to `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`:

```python
def test_claude_adapter_readme_defines_reconstruction_boundary() -> None:
    text = _read("integrations/claude/README.md")

    assert "# Claude Adapter" in text
    assert "Claude Code adapter work is future adapter work." in text
    assert "It should reconstruct Claude-specific surfaces from the `AgriciDaniel/claude-obsidian` reference implementation without moving those surfaces into neutral core." in text
    assert "## Command Mapping Baseline" in text
    assert "| `/wiki` | `llm-wiki init`, `llm-wiki continue`, or a specific `/wiki` subcommand depending on vault state |" in text
    assert "| `/save` | `llm-wiki save <vault> --title \"...\" --content \"...\"` |" in text
    assert "Claude Code hooks are adapter-only." in text
    assert "Claude Code subagents are adapter-only." in text
    assert "No `.claude-plugin` package is generated in R4.2." in text


def test_capability_mapping_records_r4_2_parity_layers() -> None:
    text = _read("docs/capability-mapping.md")

    assert "| Capability | Layer | Current status | Codex adapter behavior | Claude adapter behavior | Boundary |" in text
    assert "| Adapter parity baseline | Docs + tests | R4.2 complete | Natural-language triggers map to neutral commands | Slash-command intent maps to neutral commands | Artifact-level parity; no byte-for-byte parity |" in text
    assert "| Claude slash commands | Claude adapter | Planned after R4.2 | No Codex dependency | Wrap `/wiki` and `/save` around neutral commands | Adapter-only |" in text
    assert "| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Keep as future Claude-only reconstruction | Adapter-only; never neutral core |" in text
    assert "| Autoresearch | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |" in text
    assert "| Canvas workflows | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |" in text
    assert "| DragonScale or log-folding memory | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |" in text


def test_capability_mapping_does_not_overclaim_claude_obsidian_parity() -> None:
    text = _read("docs/capability-mapping.md").lower()

    forbidden_claims = [
        "full claude-obsidian parity is complete",
        "claude hooks are neutral core",
        "claude subagents are neutral core",
        "autoresearch is implemented",
        "canvas workflows are implemented",
        "dragonscale is implemented",
    ]
    for claim in forbidden_claims:
        assert claim not in text
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py::test_claude_adapter_readme_defines_reconstruction_boundary tests/unit/test_r4_2_adapter_parity_baseline_docs.py::test_capability_mapping_records_r4_2_parity_layers tests/unit/test_r4_2_adapter_parity_baseline_docs.py::test_capability_mapping_does_not_overclaim_claude_obsidian_parity -q
```

Expected: fail because `integrations/claude/README.md` is still a placeholder and `docs/capability-mapping.md` still has the R4.1 table shape.

- [ ] **Step 3: Replace the Claude adapter README**

Replace `integrations/claude/README.md` with this content:

```markdown
# Claude Adapter

Claude Code adapter work is future adapter work.

It should reconstruct Claude-specific surfaces from the `AgriciDaniel/claude-obsidian` reference implementation without moving those surfaces into neutral core.

## Role

The Claude adapter should map Claude Code interaction patterns to the same neutral `llm-wiki-core` operations used by the Codex adapter.

The neutral core owns durable Markdown Wiki artifacts. The Claude adapter owns Claude Code ergonomics.

## Command Mapping Baseline

| Claude surface | Neutral target |
|---|---|
| `/wiki` | `llm-wiki init`, `llm-wiki continue`, or a specific `/wiki` subcommand depending on vault state |
| `/wiki transport` | `llm-wiki detect-transport <vault>` |
| `/wiki status` | `llm-wiki status <vault>` |
| `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |
| `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |
| `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |
| `/wiki search <query>` | `llm-wiki search <vault> "<query>"` |
| `/wiki query <question>` | `llm-wiki query <vault> "<question>"` |
| `/wiki lint` | `llm-wiki lint <vault>` |
| `/save` | `llm-wiki save <vault> --title "..." --content "..."` |

## Adapter-Only Behavior

Claude Code hooks are adapter-only.

Claude Code subagents are adapter-only.

Claude slash commands are adapter-only.

No `.claude-plugin` package is generated in R4.2.

No Claude hook or subagent file is generated in R4.2.

## Deferred Reference Features

The following `AgriciDaniel/claude-obsidian` reference features remain deferred until separate designs approve them:

- `autoresearch`;
- canvas workflows;
- hybrid retrieval and reranking;
- DragonScale or log-folding memory;
- methodology modes;
- Obsidian-specific dashboards, bases, plugins, and advanced templates;
- automatic Git commits.

## Parity Rule

Claude and Codex should target artifact-level parity: compatible vault structure, raw-source rules, metadata, wikilinks, index, log, hot context, query behavior, save behavior, and lint health.

Byte-for-byte LLM prose parity is not required.
```

- [ ] **Step 4: Update capability mapping**

Replace `docs/capability-mapping.md` with this content:

```markdown
# Capability Mapping

This document maps LLM Wiki capabilities to neutral core, Codex adapter, Claude adapter, or deferred extension work.

| Capability | Layer | Current status | Codex adapter behavior | Claude adapter behavior | Boundary |
|---|---|---|---|---|---|
| Vault scaffold | Core + adapter | Complete | Map setup triggers to `llm-wiki init` | Map `/wiki` on a new vault to `llm-wiki init` | Adapter owns entry wording; core owns artifacts |
| Raw source preservation | Core | Complete | Remind Codex not to modify `.raw/` | Remind Claude not to modify `.raw/` | Raw source mutation is forbidden |
| Local file ingest | Core | Complete | Map source triggers to `llm-wiki ingest` | Map `/wiki ingest <source>` to `llm-wiki ingest` | Source must be under `.raw/` |
| Batch ingest | Core | R3.1 complete | Map folder triggers to `llm-wiki ingest-batch` | Map `/wiki ingest-batch <source-root>` to `llm-wiki ingest-batch` | Reuses core ingest behavior |
| URL ingest | Core | R3.2 complete | Map URL triggers to `llm-wiki ingest-url` | Map `/wiki ingest-url <url>` to `llm-wiki ingest-url` | One explicit URL; no crawling |
| Search durable wiki pages | Core | R3.3 complete | Map search triggers to `llm-wiki search` | Map `/wiki search <query>` to `llm-wiki search` | Read-only; no raw-source search by default |
| Query wiki | Core | Complete | Map question triggers to `llm-wiki query` | Map `/wiki query <question>` to `llm-wiki query` | Reads hot/index and ranked pages |
| Save durable insight | Core + adapter | Complete | Map save triggers to `llm-wiki save` | Map `/save` to `llm-wiki save` | Save durable knowledge, not chat noise |
| Lint wiki | Core | Complete | Map lint triggers to `llm-wiki lint` | Map `/wiki lint` to `llm-wiki lint` | Reports health and gaps |
| Adapter parity baseline | Docs + tests | R4.2 complete | Natural-language triggers map to neutral commands | Slash-command intent maps to neutral commands | Artifact-level parity; no byte-for-byte parity |
| Codex AGENTS template | Codex adapter | Complete | Provide repo-local bootstrap instructions | No Claude dependency | Adapter-only |
| Codex user-level skill | Codex adapter | R4.1 complete | Provide explicit user-level skill install helpers | No Claude dependency | Opt-in only; does not mutate global config automatically |
| Codex plugin package | Codex adapter | Deferred | Keep as future target | No Claude dependency | Not marketplace-ready through R4.2 |
| Claude schema guidance | Claude adapter | Planned after R4.2 | No Codex dependency | Future `CLAUDE.md` or equivalent schema guidance | Adapter-only |
| Claude slash commands | Claude adapter | Planned after R4.2 | No Codex dependency | Wrap `/wiki` and `/save` around neutral commands | Adapter-only |
| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Keep as future Claude-only reconstruction | Adapter-only; never neutral core |
| Autoresearch | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
| Canvas workflows | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
| Vector or hybrid retrieval | Deferred extension | Deferred | Do not claim support | Do not claim support | Future retrieval design |
| DragonScale or log-folding memory | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
| Methodology modes | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
```

- [ ] **Step 5: Run focused R4.2 tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py -q
```

Expected: `8 passed`.

- [ ] **Step 6: Commit Task 2**

Run:

```powershell
git add integrations/claude/README.md docs/capability-mapping.md tests/unit/test_r4_2_adapter_parity_baseline_docs.py
git commit -m "明确 R4.2 Claude 适配器重建边界"
```

---

### Task 3: Roadmap And Cross-Document Guardrails

**Files:**
- Modify: `docs/roadmap.md`
- Modify: `docs/roadmap-schedule.md`
- Modify: `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`

**Interfaces:**
- Consumes: parity doc and Claude boundary docs from Tasks 1 and 2
- Produces: roadmap state and cross-document guardrails that keep R4.2 claims stable

- [ ] **Step 1: Add failing roadmap and process-doc tests**

Append this content to `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`:

```python
R4_2_PUBLIC_DOCS = [
    "docs/adapter-parity-baseline.md",
    "docs/capability-mapping.md",
    "docs/roadmap.md",
    "docs/roadmap-schedule.md",
    "integrations/claude/README.md",
]

R4_2_PROCESS_DOCS = [
    "docs/superpowers/specs/2026-07-02-r4-2-adapter-parity-baseline-design.md",
    "docs/superpowers/plans/2026-07-02-r4-2-adapter-parity-baseline.md",
]


def test_r4_2_public_docs_have_no_private_paths_or_damaged_text() -> None:
    damaged = ["\ufffd", "闁", "娑", "閻", "闂", "濡ょ姴鐭侀惁"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\"]

    for relative in R4_2_PUBLIC_DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"


def test_r4_2_process_docs_have_no_private_workspace_paths() -> None:
    private_workspace_markers = [
        "D:" + "/ai/llmWiki",
        "D:" + "\\ai\\llmWiki",
        "C:" + "/Users/Administrator",
        "C:" + "\\Users\\Administrator",
    ]

    for relative in R4_2_PROCESS_DOCS:
        text = _read(relative)
        assert not [marker for marker in private_workspace_markers if marker in text], relative


def test_roadmap_records_r4_2_adapter_parity_baseline() -> None:
    roadmap = _read("docs/roadmap.md")
    schedule = _read("docs/roadmap-schedule.md")

    assert "R4.2 adapter parity baseline is complete for documentation and guard tests." in roadmap
    assert "Artifact-level Codex / Claude parity is the target; byte-for-byte LLM prose parity is not." in roadmap
    assert "Claude adapter reconstruction remains future adapter implementation work." in roadmap
    assert "### R4.2: Adapter Parity Baseline" in schedule
    assert "Status: complete." in schedule
    assert "Public adapter parity baseline document." in schedule
    assert "Claude adapter reconstruction boundary." in schedule
    assert "Guard tests against full `claude-obsidian` parity claims." in schedule
```

- [ ] **Step 2: Run the added tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py::test_roadmap_records_r4_2_adapter_parity_baseline tests/unit/test_r4_2_adapter_parity_baseline_docs.py::test_r4_2_public_docs_have_no_private_paths_or_damaged_text tests/unit/test_r4_2_adapter_parity_baseline_docs.py::test_r4_2_process_docs_have_no_private_workspace_paths -q
```

Expected: roadmap test fails because R4.2 is not recorded yet. Hygiene tests should pass unless a doc introduced private paths or damaged text.

- [ ] **Step 3: Update `docs/roadmap.md`**

In the Adapter Roadmap section, replace the current R4 text with wording that includes these exact lines:

```markdown
Codex adapter packaging readiness is complete for repo-local and documented user-level skill usage.
R4.1 explicit user-level skill installation is complete for local Codex App and Codex CLI use.
R4.2 adapter parity baseline is complete for documentation and guard tests.

Artifact-level Codex / Claude parity is the target; byte-for-byte LLM prose parity is not.

Remaining adapter work:

- Optional marketplace-grade Codex plugin packaging.
- Claude adapter reconstruction remains future adapter implementation work.
- Claude Code commands, hooks, and subagents remain adapter-only behavior.
```

- [ ] **Step 4: Update `docs/roadmap-schedule.md`**

Under `## R4: Adapter Expansion`, set the R4 status line to:

```markdown
Status: R4.2 complete; remaining R4.x adapter implementation work deferred.
```

Add this section after R4.1:

```markdown
### R4.2: Adapter Parity Baseline

Window: 2026-07-02

Status: complete.

Scope:

- Public adapter parity baseline document.
- Claude adapter reconstruction boundary.
- Capability mapping for neutral core, Codex adapter, Claude adapter, and deferred extensions.
- Guard tests against full `claude-obsidian` parity claims.
- Guard tests for artifact-level parity rather than byte-for-byte parity.

Completed outcome:

- Documented Karpathy's LLM Wiki gist as the canonical abstract pattern.
- Documented `AgriciDaniel/claude-obsidian` as the Claude Code + Obsidian reference implementation case.
- Defined Codex and Claude command intent mapping to the same neutral core operations.
- Kept Claude hooks, Claude subagents, `.claude-plugin`, autoresearch, canvas, hybrid retrieval, DragonScale, methodology modes, and marketplace-grade Codex plugin packaging deferred.

Non-scope:

- `.claude-plugin` generation.
- Claude Code hooks.
- Claude Code subagents.
- Marketplace-grade Codex plugin packaging.
- Autoresearch, canvas, hybrid retrieval, DragonScale, and methodology modes.

Exit criteria:

- Adapter parity claims are public, tested, and limited to artifact-level parity.
```

- [ ] **Step 5: Run R4.2 docs tests and adjacent adapter docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_r4_1_user_skill_install_docs.py -q
```

Expected: all tests pass with no skips required for these docs tests.

- [ ] **Step 6: Commit Task 3**

Run:

```powershell
git add docs/roadmap.md docs/roadmap-schedule.md tests/unit/test_r4_2_adapter_parity_baseline_docs.py
git commit -m "记录 R4.2 适配器等效路线图"
```

---

### Task 4: Final R4.2 Verification And Progress Record

**Files:**
- Modify: external `../codex_doc/project_understanding_progress.md`
- No repository code changes unless verification exposes a defect.

**Interfaces:**
- Consumes: R4.2 task commits.
- Produces: verified branch state and an external progress record.

- [ ] **Step 1: Run focused R4.2 tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py -q
```

Expected: all R4.2 tests pass.

- [ ] **Step 2: Run adjacent adapter docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_r4_1_user_skill_install_docs.py tests/unit/test_codex_adapter_assets.py -q
```

Expected: all selected adapter docs and asset tests pass.

- [ ] **Step 3: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with existing platform skips allowed.

- [ ] **Step 4: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no whitespace errors.

- [ ] **Step 5: Confirm dependency boundary**

Run:

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies = \\[\\]"
```

Expected output includes:

```text
dependencies = []
```

- [ ] **Step 6: Confirm branch status and recent commits**

Run:

```powershell
git status --short --branch
git log --oneline -8
```

Expected:

- branch is `r4-2-adapter-parity-baseline-design`;
- working tree is clean before final report;
- recent R4.2 commits use Chinese commit messages.

- [ ] **Step 7: Update external progress document**

Append a stage to external `../codex_doc/project_understanding_progress.md` recording:

- R4.2 implementation commits;
- focused R4.2 test result;
- adjacent adapter docs test result;
- full test result;
- whitespace check result;
- dependency boundary result;
- remaining deferred boundaries.

Use this wording as the stage body:

```markdown
## 阶段 127：R4.2 Adapter Parity Baseline 实现完成

- 分支：`r4-2-adapter-parity-baseline-design`
- 任务：完成 R4.2 公开等效基线文档、Claude adapter 重建边界、capability mapping 与路线图守护测试。
- 提交：记录本阶段 R4.2 implementation commits。
- 结果：明确 Karpathy LLM Wiki gist 是 canonical abstract pattern，`AgriciDaniel/claude-obsidian` 是 Claude Code + Obsidian reference implementation case；Codex 与 Claude 只承诺 artifact-level parity，不承诺 byte-for-byte parity 或 full `claude-obsidian` parity。
- 边界：`.claude-plugin`、Claude hooks、Claude subagents、marketplace-grade Codex plugin、autoresearch、canvas、hybrid retrieval、DragonScale、methodology modes、automatic Git commits、remote Codex Web 均仍 deferred。
- 验证：记录 focused R4.2 tests、adjacent adapter docs tests、full suite、`git diff --check`、`pyproject.toml dependencies = []` 的实际结果。
```

- [ ] **Step 8: Report final R4.2 status**

Report:

- branch name;
- latest commit hash;
- focused R4.2 test result;
- adjacent adapter docs test result;
- full suite result;
- whitespace check result;
- dependency boundary result;
- reminder that R4.2 is a docs and guard-test milestone, not a Claude adapter runtime implementation.
