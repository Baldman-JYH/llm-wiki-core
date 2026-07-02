# R4.0 Codex Adapter Packaging Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Codex adapter packaging path readable, current with R3.3 search, and verifiable without changing neutral core behavior.

**Architecture:** This is a documentation and adapter-assets readiness slice. Public docs, Codex adapter docs, Codex skill content, and guard tests are updated while the Python core operation layer remains unchanged.

**Tech Stack:** Markdown, Python 3.10+ standard library, `pytest`, existing `argparse` CLI, existing Codex adapter assets under `integrations/codex/`.

## Global Constraints

- R4.0 must not add runtime dependencies; `pyproject.toml` must keep `dependencies = []`.
- R4.0 must not change neutral core operation behavior.
- R4.0 must not implement Claude adapter reconstruction.
- R4.0 must not implement marketplace-grade Codex plugin publication.
- R4.0 must not implement vector search, hybrid retrieval, reranking, qmd integration, raw-source search by default, or LLM synthesis.
- README and adapter-facing docs must avoid local private paths and damaged historical text.
- Codex adapter assets must include current R3.3 `search`, `ingest-batch`, and `ingest-url` behavior.
- Slash commands are a target UX layer; natural-language triggers remain the required path.
- Windows support must not require WSL or Git Bash.
- Commit messages must be written in Chinese.

---

## File Structure

- Modify `README.md`: rewrite as readable English public project entrypoint for `v0.2.0-mvp`.
- Modify `tests/unit/test_readme_hygiene.py`: replace historical damaged-heading assertions with readable public-doc assertions.
- Modify `integrations/codex/skills/llm-wiki/SKILL.md`: add R3.3/R3.2/R3.1 current commands and mappings.
- Modify `integrations/codex/AGENTS.template.md`: add `ingest-batch`, `ingest-url`, and `search`.
- Modify `integrations/codex/COMMANDS.md`: expand mapping table with target slash command, CLI command, mutation behavior, and key files.
- Modify `tests/unit/test_codex_adapter_assets.py`: strengthen adapter asset guard tests.
- Modify `docs/adapter-packaging-plan.md`: rewrite current adapter packaging plan in readable English.
- Modify `docs/capability-mapping.md`: replace damaged public-facing capability summary with readable current-layer mapping.
- Modify `docs/agent-behavioral-contract.md`: replace damaged public-facing behavior contract with readable current adapter/core rules.
- Modify `integrations/codex/README.md`: document repo-local and user-level skill modes.
- Modify `integrations/codex/skills/README.md`: document skill package contents and install verification.
- Modify `integrations/codex/plugin/README.md`: document plugin packaging decision and non-goals.
- Modify `integrations/codex/install/README.md`: remove local-path examples and add portable examples.
- Modify `tests/unit/test_codex_installer_smoke.py`: keep dry-run coverage and reject private/local path examples in install docs.
- Create `tests/unit/test_r4_0_adapter_packaging_docs.py`: guard adapter packaging docs, user-level skill docs, plugin decision, and damaged-text markers.

---

### Task 1: Public README Hygiene

**Files:**
- Modify: `README.md`
- Modify: `tests/unit/test_readme_hygiene.py`

**Interfaces:**
- Consumes: current public README and R4.0 design spec.
- Produces: a readable public README and tests that guard it.

- [ ] **Step 1: Write failing README hygiene tests**

Replace `tests/unit/test_readme_hygiene.py` with:

```python
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_is_public_project_friendly() -> None:
    readme = _readme()

    forbidden_patterns = [
        r"\b[A-Z]:[\\/]",
        r"D:/",
        r"D:\\",
        r"C:/",
        r"C:\\",
        r"\\path\\to\\vault",
        r"/path/to/vault",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, readme), f"README contains local path pattern: {pattern}"

    assert "[Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)" in readme
    assert "[AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)" in readme
    assert "does not claim full parity with `claude-obsidian`" in readme


def test_readme_has_readable_public_sections() -> None:
    readme = _readme()

    required_sections = [
        "## Project Positioning",
        "## Capabilities",
        "## Quick Start",
        "## Command Reference",
        "## Artifact Layout",
        "## Codex Adapter",
        "## Current Boundaries",
        "## Roadmap",
        "## Development",
        "## License",
    ]
    for section in required_sections:
        assert section in readme


def test_readme_avoids_damaged_text_and_compatibility_anchors() -> None:
    readme = _readme()

    forbidden_fragments = [
        "Compatibility anchors",
        "\ufffd",
        "锟",
        "鈧",
        "鎼",
        "銆",
        "乣",
        "琛",
        "闃",
        "鐘",
        "楠岃瘉",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in readme


def test_readme_documents_current_r3_3_and_v0_2_mvp_scope() -> None:
    readme = _readme()

    assert "Current release: `v0.2.0-mvp`" in readme
    assert 'llm-wiki search <vault> "durable wiki knowledge"' in readme
    assert "R3.3 search is read-only and searches durable Markdown wiki pages by default." in readme
    assert "Vector search, hybrid retrieval, reranking, raw-source search by default, qmd integration, and LLM synthesis remain deferred." in readme
    assert "The official `obsidian` CLI remains optional and verified-only; filesystem fallback stays available." in readme
```

- [ ] **Step 2: Run README tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_readme_hygiene.py -q
```

Expected: fail because current README still contains damaged compatibility anchors and unreadable headings.

- [ ] **Step 3: Rewrite README**

Replace `README.md` with readable English content containing these exact sections:

```markdown
# llm-wiki-core

`llm-wiki-core` is a neutral local LLM Wiki practice implementation. The canonical abstraction is [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): raw materials stay durable, and the agent maintains a Markdown wiki instead of leaving knowledge trapped in chat. [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) is the reference implementation for the Claude Code + Obsidian workflow, while `llm-wiki-core` focuses on a neutral, testable core that does not claim full parity with `claude-obsidian`.

Current release: `v0.2.0-mvp`. R3.3 adds local read-only wiki search on top of the R3.2 URL ingest flow.

## Project Positioning

- Karpathy's gist is the canonical abstract idea.
- `AgriciDaniel/claude-obsidian` is the Claude Code + Obsidian reference implementation.
- `llm-wiki-core` is a neutral practice implementation for Codex App, Codex CLI, and future local agents.

## Capabilities

- Initialize a standard local LLM Wiki vault.
- Preserve raw source inputs under `.raw/`.
- Track source metadata and provenance in `.raw/.manifest.json`.
- Ingest one local Markdown source with `ingest`.
- Ingest local Markdown folders with `ingest-batch`.
- Ingest one explicit URL into an immutable `.raw/url/` snapshot with `ingest-url`.
- Search durable Markdown wiki pages with dependency-free BM25-style lexical retrieval.
- Query, save, resume, and lint the wiki.
- Use filesystem transport as the default portable runtime path.
- Treat the official `obsidian` CLI as optional and verified-only.

## Quick Start

### Install

```powershell
git clone https://github.com/Baldman-JYH/llm-wiki-core.git
cd llm-wiki-core
python -m pip install -e .
python -m llm_wiki_core --version
```

### Initialize A Vault

```powershell
llm-wiki init <vault> --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport <vault> --force
```

### Ingest Sources

```powershell
llm-wiki ingest <vault> .raw/articles/example.md
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-url <vault> https://example.com/article
```

### Search, Query, And Maintain

```powershell
llm-wiki status <vault>
llm-wiki continue <vault>
llm-wiki search <vault> "durable wiki knowledge"
llm-wiki query <vault> "What does the wiki know about this source?"
llm-wiki save <vault> --title "Saved Insight" --content "Durable insight text."
llm-wiki lint <vault>
```

## Command Reference

| Command | Purpose |
|---|---|
| `llm-wiki init <vault> --purpose "..."` | Initialize a local wiki vault. |
| `llm-wiki detect-transport <vault> --force` | Record runtime transport capability metadata. |
| `llm-wiki ingest <vault> <source>` | Ingest one local Markdown source under `.raw/`. |
| `llm-wiki ingest-batch <vault> <source-root>` | Ingest local Markdown files discovered under `.raw/`. |
| `llm-wiki ingest-url <vault> <url>` | Fetch one explicit URL, store an immutable `.raw/url/` snapshot, and ingest the normalized Markdown source. |
| `llm-wiki status <vault>` | Inspect initialization and source status. |
| `llm-wiki continue <vault>` | Re-enter current wiki context. |
| `llm-wiki search <vault> "<query>"` | Search ranked local wiki pages with dependency-free BM25-style lexical retrieval. |
| `llm-wiki query <vault> "<question>"` | Query the wiki using current wiki context and ranked pages. |
| `llm-wiki save <vault> --content "..."` | Save durable insight back into the wiki. |
| `llm-wiki lint <vault>` | Check wiki health and write a lint report. |

## Artifact Layout

```text
<vault>/
  AGENTS.md
  .raw/
    .manifest.json
    url/
  wiki/
    index.md
    log.md
    hot.md
    overview.md
    sources/
    entities/
    concepts/
    questions/
    comparisons/
    meta/
```

- `.raw/` stores preserved raw inputs.
- `.raw/url/` stores immutable URL ingest snapshots.
- `wiki/` stores durable Markdown knowledge artifacts.

## Codex Adapter

The Codex adapter assets live under `integrations/codex/`. Repo-local install scripts initialize a vault and print re-entry commands. User-level skill packaging is being prepared in R4.0.

Codex entry points must call the neutral core commands instead of redefining LLM Wiki behavior. Natural-language triggers are required; slash commands are a target UX layer.

## Documentation

- [User Guide](docs/user-guide.md)
- [Operation Contract](docs/operation-contract.md)
- [Codex Command Contract](docs/codex-command-contract.md)
- [Manifest Schema](docs/manifest-schema.md)
- [Roadmap Schedule](docs/roadmap-schedule.md)
- [Completion Criteria](docs/completion-criteria.md)
- [Release Readiness Checklist](docs/release-readiness-checklist.md)
- [Archive Manifest](docs/archive-manifest.md)

## Current Boundaries

- URL ingest creates immutable `.raw/url/` snapshots.
- R3.3 search is read-only and searches durable Markdown wiki pages by default.
- R3.3 uses dependency-free BM25-style lexical retrieval.
- R3.3 remains text-first on top of the R3.2 URL ingest foundation.
- Vector search, hybrid retrieval, reranking, raw-source search by default, qmd integration, and LLM synthesis remain deferred.
- Full readability, defuddle, JavaScript rendering, authenticated pages, and crawling remain deferred.
- Binary or non-decodable responses are rejected instead of being archived through the text transport.
- The official `obsidian` CLI remains optional and verified-only; filesystem fallback stays available.

## Roadmap

- R1: hardening.
- R2: verified optional runtime transport for the official `obsidian` CLI.
- R3: ingest and retrieval expansion, including local Markdown batch ingest, URL ingest, and local wiki search.
- R4: adapter expansion.
- R5: knowledge-organization extensions.

See [docs/roadmap-schedule.md](docs/roadmap-schedule.md) for the prioritized schedule.

## Development

```powershell
python -m pip install -e .
python -m pytest
```

## License

The repository does not yet ship a final `LICENSE` file.
```

- [ ] **Step 4: Run README tests**

Run:

```powershell
python -m pytest tests/unit/test_readme_hygiene.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit Task 1**

```powershell
git add README.md tests/unit/test_readme_hygiene.py
git commit -m "清理 R4.0 README 公开文档"
```

---

### Task 2: Codex Adapter Assets Current Command Coverage

**Files:**
- Modify: `integrations/codex/skills/llm-wiki/SKILL.md`
- Modify: `integrations/codex/AGENTS.template.md`
- Modify: `integrations/codex/COMMANDS.md`
- Modify: `tests/unit/test_codex_adapter_assets.py`

**Interfaces:**
- Consumes: R3.3 current core commands and `docs/codex-command-contract.md`.
- Produces: Codex adapter assets that map natural language to current CLI commands.

- [ ] **Step 1: Write failing adapter asset tests**

Replace `tests/unit/test_codex_adapter_assets.py` with:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_codex_skill_references_current_commands_and_search_mapping() -> None:
    text = _read("integrations/codex/skills/llm-wiki/SKILL.md")

    for command in [
        "llm-wiki init",
        "llm-wiki detect-transport",
        "llm-wiki status",
        "llm-wiki continue",
        "llm-wiki ingest",
        "llm-wiki ingest-batch",
        "llm-wiki ingest-url",
        "llm-wiki search",
        "llm-wiki query",
        "llm-wiki save",
        "llm-wiki lint",
    ]:
        assert command in text

    assert "search wiki for X" in text
    assert "find wiki pages about X" in text
    assert "Search is read-only" in text
    assert "artifact-level equivalence" in text


def test_codex_agents_template_references_current_workflow() -> None:
    text = _read("integrations/codex/AGENTS.template.md")

    for command in [
        "llm-wiki init",
        "llm-wiki detect-transport",
        "llm-wiki status",
        "llm-wiki continue",
        "llm-wiki ingest",
        "llm-wiki ingest-batch",
        "llm-wiki ingest-url",
        "llm-wiki search",
        "llm-wiki query",
        "llm-wiki save",
        "llm-wiki lint",
    ]:
        assert command in text

    assert ".raw/" in text
    assert "wiki/index.md" in text
    assert "wiki/log.md" in text
    assert "wiki/hot.md" in text


def test_codex_command_mapping_documents_search_and_mutation_behavior() -> None:
    text = _read("integrations/codex/COMMANDS.md")

    assert "| Natural language trigger | Target slash command | CLI command | Mutation behavior | Key files |" in text
    assert "| search wiki for X | `/wiki search <query>` | `llm-wiki search <vault> \"X\"` | read-only | `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/questions/`, `wiki/comparisons/` |" in text
    assert "| ingest this URL | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` | writes raw snapshot and wiki artifacts | `.raw/url/`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |" in text
    assert "Natural language triggers are required; slash commands are a target UX layer." in text


def test_codex_command_mapping_table_rows_are_well_formed() -> None:
    text = _read("integrations/codex/COMMANDS.md")
    rows = [
        line
        for line in text.splitlines()
        if line.startswith("|") and not set(line.replace("|", "").strip()) <= {"-"}
    ]

    assert rows
    expected_columns = rows[0].count("|")
    for row in rows:
        assert row.endswith("|")
        assert row.count("|") == expected_columns


def test_codex_install_entrypoints_exist() -> None:
    ps1 = _read("integrations/codex/install/install.ps1")
    sh = _read("integrations/codex/install/install.sh")

    assert "llm-wiki init" in ps1
    assert "llm-wiki init" in sh
    assert "pip install -e" in ps1
    assert "pip install -e" in sh
```

- [ ] **Step 2: Run adapter asset tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_codex_adapter_assets.py -q
```

Expected: fail because current Codex skill and command mapping do not include `search`, `ingest-batch`, or `ingest-url` coverage.

- [ ] **Step 3: Update Codex skill**

Replace `integrations/codex/skills/llm-wiki/SKILL.md` with:

```markdown
---
name: llm-wiki
description: Maintain a local LLM Wiki vault from Codex App or Codex CLI. Triggers on set up wiki, scaffold vault, check transport, check wiki status, continue wiki, resume wiki context, ingest this source, ingest this folder, ingest this URL, search wiki for, find wiki pages about, query the wiki, what does the wiki know about, save this insight, lint the wiki.
---

# LLM Wiki

Use this skill when the user wants Codex to maintain a local LLM Wiki vault.

The wiki is the durable artifact. Chat is the interface.

## Core Rules

- Treat `.raw/` as immutable source material.
- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.
- Use the neutral `llm-wiki` core commands instead of redefining behavior in the adapter.
- Natural-language triggers are required; slash commands are a target UX layer.

## Commands

- `llm-wiki init <vault> --purpose "..."`
- `llm-wiki detect-transport <vault>`
- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`
- `llm-wiki ingest <vault> <source-under-.raw>`
- `llm-wiki ingest-batch <vault> <source-root-under-.raw>`
- `llm-wiki ingest-url <vault> <url>`
- `llm-wiki search <vault> "<query>"`
- `llm-wiki query <vault> "<question>"`
- `llm-wiki save <vault> --title "..." --content "..."`
- `llm-wiki lint <vault>`

## Natural Language Mapping

- "set up wiki" or "scaffold vault" means run init.
- "check transport" means run detect-transport.
- "check wiki status" means run status.
- "continue wiki" or "resume wiki context" means run continue.
- "ingest this source" means run ingest.
- "ingest this folder" means run ingest-batch.
- "ingest this URL" means run ingest-url.
- "search wiki for X" or "find wiki pages about X" means run search.
- "what does the wiki know about X" means run query.
- "save this insight" means run save.
- "lint the wiki" means run lint.

## Search Behavior

Search is read-only. It ranks durable Markdown wiki pages and returns page paths, titles, snippets, matched terms, and scores before query synthesis.

## Boundaries

- Do not modify Raw Source files.
- Do not generate Claude-specific plugin files.
- Do not claim semantic deep retrieval, vector search, hybrid retrieval, reranking, qmd integration, or LLM synthesis.
- Do not treat slash commands as the only entry path.
```

- [ ] **Step 4: Update AGENTS template**

Replace the command list and trigger list in `integrations/codex/AGENTS.template.md` so the file contains:

```markdown
# LLM Wiki Agent Instructions

Use this vault according to the LLM Wiki pattern:

- Treat `.raw/` as immutable source material.
- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.
- Follow the operation contracts in `docs/operation-contract.md`.

## Commands

Use the local `llm-wiki` CLI when available:

- `llm-wiki init <vault> --purpose "..."`
- `llm-wiki detect-transport <vault>`
- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`
- `llm-wiki ingest <vault> <source-under-.raw>`
- `llm-wiki ingest-batch <vault> <source-root-under-.raw>`
- `llm-wiki ingest-url <vault> <url>`
- `llm-wiki search <vault> "<query>"`
- `llm-wiki query <vault> "<question>"`
- `llm-wiki save <vault> --title "..." --content "..."`
- `llm-wiki lint <vault>`

## Natural Language Triggers

- "set up wiki" -> init
- "check transport" -> detect-transport
- "check wiki status" -> status
- "continue wiki" -> continue
- "resume wiki context" -> continue
- "ingest this source" -> ingest
- "ingest this folder" -> ingest-batch
- "ingest this URL" -> ingest-url
- "search wiki for X" -> search
- "find wiki pages about X" -> search
- "what does the wiki know about X" -> query
- "save this insight" -> save
- "lint the wiki" -> lint
```

- [ ] **Step 5: Update command mapping**

Replace `integrations/codex/COMMANDS.md` with:

```markdown
# Codex Command Mapping

This document maps Codex App / CLI natural language triggers to local `llm-wiki` commands. Natural language triggers are required; slash commands are a target UX layer.

| Natural language trigger | Target slash command | CLI command | Mutation behavior | Key files |
|---|---|---|---|---|
| set up wiki | `/wiki` | `llm-wiki init <vault> --purpose "..."` | writes vault scaffold | `AGENTS.md`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| scaffold vault | `/wiki` | `llm-wiki init <vault> --purpose "..."` | writes vault scaffold | `AGENTS.md`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| check transport | `/wiki transport` | `llm-wiki detect-transport <vault>` | writes transport snapshot | `wiki/meta/transport.json` |
| check wiki status | `/wiki status` | `llm-wiki status <vault>` | read-only | `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| continue wiki | `/wiki` | `llm-wiki continue <vault>` | read-only | `wiki/hot.md`, `wiki/index.md`, `wiki/log.md` |
| resume wiki context | `/wiki` | `llm-wiki continue <vault>` | read-only | `wiki/hot.md`, `wiki/index.md`, `wiki/log.md` |
| ingest this source | `/wiki ingest <source>` | `llm-wiki ingest <vault> <source-under-.raw>` | writes wiki artifacts | `.raw/.manifest.json`, `wiki/sources/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| ingest this folder | `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` | writes wiki artifacts | `.raw/.manifest.json`, `wiki/sources/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| ingest this URL | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` | writes raw snapshot and wiki artifacts | `.raw/url/`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| search wiki for X | `/wiki search <query>` | `llm-wiki search <vault> "X"` | read-only | `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/questions/`, `wiki/comparisons/` |
| find wiki pages about X | `/wiki search <query>` | `llm-wiki search <vault> "X"` | read-only | `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/questions/`, `wiki/comparisons/` |
| what does the wiki know about X | `/wiki query <question>` | `llm-wiki query <vault> "X"` | read-only | `wiki/hot.md`, `wiki/index.md`, ranked wiki pages |
| save this insight | `/wiki save [title]` | `llm-wiki save <vault> --title "..." --content "..."` | writes wiki artifact | `wiki/questions/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| lint the wiki | `/wiki lint` | `llm-wiki lint <vault>` | writes lint report | `wiki/meta/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
```

- [ ] **Step 6: Run adapter asset tests**

Run:

```powershell
python -m pytest tests/unit/test_codex_adapter_assets.py -q
```

Expected: `5 passed`.

- [ ] **Step 7: Commit Task 2**

```powershell
git add integrations/codex/skills/llm-wiki/SKILL.md integrations/codex/AGENTS.template.md integrations/codex/COMMANDS.md tests/unit/test_codex_adapter_assets.py
git commit -m "更新 R4.0 Codex 适配器命令映射"
```

---

### Task 3: Adapter Packaging Docs And Guard Tests

**Files:**
- Modify: `docs/adapter-packaging-plan.md`
- Modify: `docs/capability-mapping.md`
- Modify: `docs/agent-behavioral-contract.md`
- Modify: `integrations/codex/README.md`
- Modify: `integrations/codex/skills/README.md`
- Modify: `integrations/codex/plugin/README.md`
- Modify: `integrations/codex/install/README.md`
- Modify: `tests/unit/test_codex_installer_smoke.py`
- Create: `tests/unit/test_r4_0_adapter_packaging_docs.py`

**Interfaces:**
- Consumes: R4.0 design spec and Codex adapter assets from Task 2.
- Produces: readable adapter packaging docs and guard tests.

- [ ] **Step 1: Write failing R4.0 adapter docs tests**

Create `tests/unit/test_r4_0_adapter_packaging_docs.py`:

```python
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


PUBLIC_DOCS = [
    "docs/adapter-packaging-plan.md",
    "docs/capability-mapping.md",
    "docs/agent-behavioral-contract.md",
    "integrations/codex/README.md",
    "integrations/codex/skills/README.md",
    "integrations/codex/plugin/README.md",
    "integrations/codex/install/README.md",
]


def test_r4_0_public_adapter_docs_have_no_damaged_text_or_private_paths() -> None:
    damaged = ["\ufffd", "锟", "鈧", "鎼", "銆", "乣", "琛", "闃", "鐘", "楠岃瘉"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\"]

    for relative in PUBLIC_DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"


def test_adapter_packaging_plan_documents_install_modes_and_plugin_decision() -> None:
    text = _read("docs/adapter-packaging-plan.md")

    assert "## Packaging Goals" in text
    assert "## Repo-Local Mode" in text
    assert "## User-Level Skill Mode" in text
    assert "## Plugin Packaging Decision" in text
    assert "R4.0 does not publish a marketplace-grade Codex plugin." in text
    assert "neutral core must not depend on Codex adapter behavior" in text


def test_capability_mapping_keeps_core_adapter_and_claude_boundaries() -> None:
    text = _read("docs/capability-mapping.md")

    assert "| Capability | Layer | Current status | Codex adapter behavior | Boundary |" in text
    assert "| Search durable wiki pages | Core | R3.3 complete | Map search triggers to `llm-wiki search` | Read-only; no raw-source search by default |" in text
    assert "| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Adapter-only; never neutral core |" in text


def test_agent_behavioral_contract_documents_search_and_adapter_parity() -> None:
    text = _read("docs/agent-behavioral-contract.md")

    assert "## Search Behavior" in text
    assert "Search is read-only and returns ranked durable wiki pages before query synthesis." in text
    assert "## Adapter Parity" in text
    assert "Artifact-level equivalence is required; byte-for-byte LLM prose equivalence is not required." in text
    assert "Do not treat Claude-specific hooks, commands, or subagents as neutral core requirements." in text


def test_codex_integration_docs_document_user_level_skill_without_global_mutation() -> None:
    readme = _read("integrations/codex/README.md")
    skills = _read("integrations/codex/skills/README.md")
    plugin = _read("integrations/codex/plugin/README.md")

    assert "Repo-local mode" in readme
    assert "User-level skill mode" in readme
    assert "does not automatically mutate global Codex configuration" in readme
    assert "Verify the skill includes `llm-wiki search`" in skills
    assert "Plugin packaging is a future target" in plugin
    assert "not a marketplace-ready plugin" in plugin
```

- [ ] **Step 2: Update installer smoke test doc assertions**

In `tests/unit/test_codex_installer_smoke.py`, add:

```python
def test_install_readme_uses_portable_examples_not_private_paths() -> None:
    text = (_repo_root() / "integrations" / "codex" / "install" / "README.md").read_text(encoding="utf-8")

    assert "<vault>" in text
    assert "D:\\path\\to\\vault" not in text
    assert "/path/to/vault" not in text
    assert "WSL" not in text
    assert "Git Bash" not in text
```

- [ ] **Step 3: Run adapter docs tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py::test_install_readme_uses_portable_examples_not_private_paths -q
```

Expected: fail because current docs contain damaged text and local path examples.

- [ ] **Step 4: Rewrite adapter packaging plan**

Replace `docs/adapter-packaging-plan.md` with readable English sections:

```markdown
# Adapter Packaging Plan

This document defines the Codex adapter packaging strategy for R4.0.

## Packaging Goals

Codex App and Codex CLI users should be able to use the same core LLM Wiki workflow that the Claude Code + Obsidian reference implementation demonstrates: initialize a vault, ingest raw sources, search and query the wiki, lint it, save durable insights, and maintain `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, and `.raw/.manifest.json`.

The neutral core must not depend on Codex adapter behavior.

## Repo-Local Mode

Repo-local mode remains the baseline install mode. The user runs the installer from this repository, the installer performs editable package installation, initializes the target vault, detects transport, and prints re-entry commands.

## User-Level Skill Mode

User-level skill mode is the reusable Codex skill path. R4.0 documents the source skill directory, destination examples, and verification commands. R4.0 does not automatically mutate global Codex configuration.

## Plugin Packaging Decision

Plugin packaging is a future target. R4.0 does not publish a marketplace-grade Codex plugin.

A future plugin may include skill metadata, command mapping docs, install guidance, and adapter verification. It must still call neutral core commands instead of redefining LLM Wiki behavior.

## Windows Support

Windows support must be native PowerShell. It must not require WSL or Git Bash.

## macOS And Linux Support

macOS and Linux support use the portable shell installer. Shell scripts remain thin wrappers around core commands.

## Non-Goals

- Do not publish to a marketplace in R4.0.
- Do not generate Claude-specific plugin files.
- Do not modify global Codex configuration automatically.
- Do not move domain behavior into the Codex adapter.
```

- [ ] **Step 5: Rewrite capability mapping**

Replace `docs/capability-mapping.md` with:

```markdown
# Capability Mapping

This document maps LLM Wiki capabilities to neutral core, Codex adapter, Claude adapter, or deferred work.

| Capability | Layer | Current status | Codex adapter behavior | Boundary |
|---|---|---|---|---|
| Vault scaffold | Core + adapter | Complete | Map setup triggers to `llm-wiki init` | Adapter owns entry wording; core owns artifacts |
| Raw source preservation | Core | Complete | Remind Codex not to modify `.raw/` | Raw source mutation is forbidden |
| Local file ingest | Core | Complete | Map source triggers to `llm-wiki ingest` | Source must be under `.raw/` |
| Batch ingest | Core | R3.1 complete | Map folder triggers to `llm-wiki ingest-batch` | Reuses core ingest behavior |
| URL ingest | Core | R3.2 complete | Map URL triggers to `llm-wiki ingest-url` | One explicit URL; no crawling |
| Search durable wiki pages | Core | R3.3 complete | Map search triggers to `llm-wiki search` | Read-only; no raw-source search by default |
| Query wiki | Core | Complete | Map question triggers to `llm-wiki query` | Reads hot/index and ranked pages |
| Save durable insight | Core + adapter | Complete | Map save triggers to `llm-wiki save` | Save durable knowledge, not chat noise |
| Lint wiki | Core | Complete | Map lint triggers to `llm-wiki lint` | Reports health and gaps |
| Codex AGENTS template | Codex adapter | Complete | Provide repo-local bootstrap instructions | Adapter-only |
| Codex user-level skill | Codex adapter | R4.0 readiness | Provide reusable skill docs | Does not mutate global config automatically |
| Codex plugin package | Codex adapter | Deferred | Keep as future target | Not marketplace-ready in R4.0 |
| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Adapter-only; never neutral core |
| Vector or hybrid retrieval | Deferred | Deferred | Do not claim support | Future retrieval design |
```
```

- [ ] **Step 6: Rewrite agent behavioral contract**

Replace `docs/agent-behavioral-contract.md` with:

```markdown
# Agent Behavioral Contract

This document defines behavior that every LLM Wiki adapter must preserve.

## Highest Principle

The wiki is the durable artifact. Chat is only the interface.

## Startup Behavior

When entering an initialized vault, an agent should read project instructions, then `wiki/hot.md`, `wiki/index.md`, and recent `wiki/log.md` entries as needed.

## Ingest Behavior

Agents must read raw sources without modifying them, update source summaries, maintain index/log/hot, and record provenance in `.raw/.manifest.json`.

## Search Behavior

Search is read-only and returns ranked durable wiki pages before query synthesis.

## Query Behavior

Query reads `wiki/hot.md`, reads `wiki/index.md`, selects only necessary relevant pages, cites wiki pages, and reports gaps when coverage is missing.

## Save Behavior

Save durable knowledge, not transient chat noise. Saved content must update the corresponding wiki page, index, log, and hot cache.

## Lint Behavior

Lint checks frontmatter, wikilinks, orphan pages, index coverage, recent log entries, hot cache health, and manifest parseability.

## Adapter Parity

Artifact-level equivalence is required; byte-for-byte LLM prose equivalence is not required.

Adapters should produce equivalent files, metadata, links, logs, and validation results for the same operation.

## Forbidden Behavior

- Do not modify Raw Source files.
- Do not bypass index/log/hot maintenance.
- Do not treat Claude-specific hooks, commands, or subagents as neutral core requirements.
- Do not claim vector search, hybrid retrieval, reranking, qmd integration, or LLM synthesis unless those features are explicitly implemented.
```

- [ ] **Step 7: Rewrite Codex integration docs**

Update `integrations/codex/README.md` with:

```markdown
# Codex Adapter

This directory contains Codex App and Codex CLI integration assets.

The adapter calls into neutral `llm-wiki` core commands instead of redefining LLM Wiki behavior.

## Repo-local mode

Use repo-local mode when working from this repository:

```powershell
integrations/codex/install/install.ps1 -VaultPath <vault> -Purpose "Research workflow"
```

```sh
integrations/codex/install/install.sh <vault> "Research workflow"
```

## User-level skill mode

User-level skill mode copies or installs `integrations/codex/skills/llm-wiki` into a user's Codex skills directory.

R4.0 documents this mode but does not automatically mutate global Codex configuration.

## Verification

After setup, verify that Codex can trigger status, continue, ingest, search, query, save, and lint behavior through natural language.
```

Update `integrations/codex/skills/README.md` with:

```markdown
# Codex Skills

The reusable LLM Wiki skill lives in `integrations/codex/skills/llm-wiki`.

## User-Level Installation

Copy the `llm-wiki` skill directory into the Codex user skills directory for your platform.

Use the current Codex documentation for the exact destination path. R4.0 does not automatically mutate global Codex configuration.

## Verification

Verify the skill includes `llm-wiki search`, `llm-wiki ingest-batch`, and `llm-wiki ingest-url`.

Then ask Codex to:

- "check wiki status"
- "continue wiki"
- "search wiki for durable knowledge"
- "what does the wiki know about durable knowledge"
```

Update `integrations/codex/plugin/README.md` with:

```markdown
# Codex Plugin

Plugin packaging is a future target.

This directory is not a marketplace-ready plugin in R4.0. It records the intended boundary for a future Codex plugin package.

A future plugin may include skill metadata, command mapping docs, install guidance, and adapter verification, but it must keep neutral core behavior in `llm-wiki-core`.
```

Update `integrations/codex/install/README.md` with:

```markdown
# Installers

Repo-local installer entrypoints for Codex App / CLI usage.

PowerShell:

```powershell
.\install.ps1 -VaultPath <vault> -Purpose "Research workflow"
.\install.ps1 -VaultPath <vault> -Purpose "Research workflow" -DryRun
```

macOS / Linux shell:

```sh
./install.sh <vault> "Research workflow"
./install.sh --dry-run <vault> "Research workflow"
```

The installers run local editable package installation, initialize the vault, and detect transport. They print `status` and `continue` as recommended next steps.

Windows support is native PowerShell and does not require WSL or Git Bash.
```

- [ ] **Step 8: Run adapter docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py -q
```

Expected on Windows: selected tests pass with the existing POSIX shell dry-run skip.

- [ ] **Step 9: Commit Task 3**

```powershell
git add docs/adapter-packaging-plan.md docs/capability-mapping.md docs/agent-behavioral-contract.md integrations/codex/README.md integrations/codex/skills/README.md integrations/codex/plugin/README.md integrations/codex/install/README.md tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py
git commit -m "补齐 R4.0 适配器打包文档"
```

---

### Task 4: Final R4.0 Verification And Progress Record

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`
- No repository code changes unless verification exposes a defect.

**Interfaces:**
- Consumes: R4.0 task commits.
- Produces: verified branch state and an external progress record.

- [ ] **Step 1: Run focused R4.0 tests**

Run:

```powershell
python -m pytest tests/unit/test_readme_hygiene.py tests/unit/test_codex_adapter_assets.py tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_codex_installer_smoke.py -q
```

Expected on Windows: all selected tests pass with the existing POSIX shell dry-run skip.

- [ ] **Step 2: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with the existing Windows POSIX shell dry-run skip allowed.

- [ ] **Step 3: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no whitespace errors.

- [ ] **Step 4: Confirm dependency boundary**

Run:

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies = \[\]"
```

Expected output includes:

```text
dependencies = []
```

- [ ] **Step 5: Confirm branch status and log**

Run:

```powershell
git status --short --branch
git log --oneline -8
```

Expected:

- branch is `r4-0-codex-adapter-packaging-readiness-design`;
- working tree is clean before final review;
- recent R4.0 commits use Chinese commit messages.

- [ ] **Step 6: Update external progress document**

Append a new stage to `D:/ai/llmWiki/codex_doc/project_understanding_progress.md` with:

```markdown
## 阶段 107：R4.0 Codex Adapter Packaging Readiness 实施完成

状态：已完成

### 本阶段目标

完成 R4.0 Codex adapter packaging readiness：README 清理、Codex skill/search 映射、adapter docs、user-level skill packaging 文档、plugin packaging decision 和 guard tests。

### 完成内容

- README 已改为可读公开英文文档。
- Codex skill 已包含 `search`、`ingest-batch`、`ingest-url`。
- Codex command mapping 已包含 search read-only 行为。
- Adapter packaging docs 已明确 repo-local、user-level skill、plugin future target。
- Guard tests 已覆盖 damaged text、本地路径、过期命令映射和 core/adapter 边界。

### 验证结果

- 写入 Step 1 到 Step 4 的实际命令和结果。

### Git 状态

- 写入 Step 5 的实际分支、HEAD 和工作区状态。

### 下一步

进入 R4.0 final review；若通过，则推送分支并创建 PR。
```

- [ ] **Step 7: Commit progress document if it is inside repo**

The external progress document is outside the repository. Do not add it to repo git. If any `codex_doc/` appears inside `llm-wiki-core`, remove it before committing.

- [ ] **Step 8: Report final R4.0 status**

The report must include:

- branch name;
- latest commit hash;
- focused test result;
- full test result;
- whitespace check result;
- dependency boundary result;
- reminder that Claude adapter reconstruction and plugin marketplace publication remain deferred.
