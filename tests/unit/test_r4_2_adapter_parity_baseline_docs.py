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


def test_claude_adapter_readme_defines_reconstruction_boundary() -> None:
    text = _read("integrations/claude/README.md")

    assert "# Claude Adapter" in text
    assert "Claude Code adapter work is future adapter work." in text
    assert (
        "It should reconstruct Claude-specific surfaces from the `AgriciDaniel/claude-obsidian` "
        "reference implementation without moving those surfaces into neutral core." in text
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
