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
        "claude hooks are neutral core",
        "claude subagents are neutral core",
        "marketplace-grade codex plugin is complete",
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


def test_claude_adapter_readme_defines_reconstruction_boundary() -> None:
    text = _read("integrations/claude/README.md")

    assert "# Claude Adapter" in text
    assert "R4.3 ships a project-local Claude adapter MVP. Advanced Claude reconstruction remains future adapter work." in text
    assert (
        "The MVP provides project-local command surfaces derived from the `AgriciDaniel/claude-obsidian` "
        "reference implementation while keeping advanced Claude reconstruction out of neutral core." in text
    )
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
    assert (
        "| Claude advanced command surfaces | Claude adapter | Deferred | No Codex dependency | Hooks, subagents, `.claude-plugin`, "
        "autoresearch, canvas, hybrid retrieval, DragonScale, methodology modes, and related advanced command surfaces are deferred for future "
        "Claude reconstruction | Adapter-only; never neutral core |" in text
    )
    assert (
        "| Claude advanced schema guidance | Claude adapter | Deferred | No Codex dependency | Advanced `CLAUDE.md` schema, hooks/subagents, "
        "and `.claude-plugin` reconstruction remain future work | Adapter-only; never neutral core |" in text
    )
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
    damaged = ["\ufffd", "闂", "濞", "闁", "闂", "婵°倗濮撮惌渚€鎯"]
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
