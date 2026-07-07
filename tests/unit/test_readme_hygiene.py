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
        "閿",
        "閳",
        "閹",
        "閵",
        "涔",
        "鐞",
        "闂",
        "閻",
        "妤犲矁鐦",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in readme


def test_readme_documents_current_r5_0_and_v0_5_0_mvp_scope() -> None:
    readme = _readme()

    assert "Current release: `v0.5.0-mvp`" in readme
    assert "Current status: R5.0 ships the knowledge organization foundation while preserving the existing generic LLM Wiki behavior." in readme
    assert 'llm-wiki search <vault> "durable wiki knowledge"' in readme
    assert "R3.3 search is read-only and searches durable Markdown wiki pages by default." in readme
    assert "Codex user-level skill installation is explicit and does not edit global Codex configuration automatically." in readme
    assert "Claude project-local adapter installation is explicit and does not edit user-global Claude settings automatically." in readme
    assert "R5.0 knowledge organization foundation keeps `generic` as the default organization mode." in readme
    assert "LYT, PARA, Zettelkasten, DragonScale, semantic stale-claim lint, and comparison workflow helpers remain deferred." in readme
    assert "Vector search, hybrid retrieval, reranking, raw-source search by default, qmd integration, and LLM synthesis remain deferred." in readme
    assert "The official `obsidian` CLI remains optional and verified-only; filesystem fallback stays available." in readme
