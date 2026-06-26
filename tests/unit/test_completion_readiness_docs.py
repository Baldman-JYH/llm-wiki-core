from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_completion_criteria_and_roadmap_define_mvp_boundary() -> None:
    completion = _read("docs/completion-criteria.md")
    roadmap = _read("docs/roadmap.md")

    completion_terms = [
        "MVP Local Complete",
        "Karpathy",
        "claude-obsidian reference implementation",
        "artifact-level equivalence",
        "Codex App",
        "Codex CLI",
        "filesystem",
        "Obsidian CLI actual read/write/search is not implemented",
        "Full claude-obsidian parity is not the MVP completion criterion",
    ]
    for term in completion_terms:
        assert term in completion

    roadmap_terms = [
        "MVP local use",
        "Obsidian CLI actual read/write/search",
        "URL ingest",
        "batch ingest",
        "deep retrieval",
        "Claude adapter",
    ]
    for term in roadmap_terms:
        assert term in roadmap


def test_readme_links_completion_docs() -> None:
    readme = _read("README.md")

    assert "docs/completion-criteria.md" in readme
    assert "docs/roadmap.md" in readme


def test_legacy_obsidian_cli_preferred_runtime_claims_are_removed() -> None:
    checked_docs = [
        "docs/mvp-scope.md",
        "docs/capability-mapping.md",
        "docs/milestone-plan.md",
    ]
    stale_phrases = [
        "检测 Obsidian CLI，并在可用时优先使用",
        "在有 Obsidian CLI 的机器上，MVP 优先使用 CLI",
        "有 Obsidian CLI 时 preferred 为 cli",
        "Obsidian CLI optional transport",
        "可选优先，失败回退 filesystem",
    ]

    for relative in checked_docs:
        text = _read(relative)
        for phrase in stale_phrases:
            assert phrase not in text, f"{phrase!r} remains in {relative}"
