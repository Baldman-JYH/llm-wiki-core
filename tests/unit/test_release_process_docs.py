from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_mvp_release_notes_capture_local_release_boundary() -> None:
    notes = _read("docs/release-notes-v0.1.0-mvp.md")

    required_terms = [
        "v0.1.0-mvp",
        "MVP Local Complete",
        "Codex App",
        "Codex CLI",
        "artifact-level equivalence",
        "filesystem",
        "Obsidian CLI actual read/write/search is not implemented",
        "Full claude-obsidian parity is not included",
    ]
    for term in required_terms:
        assert term in notes


def test_archive_manifest_defines_release_artifact_policy() -> None:
    manifest = _read("docs/archive-manifest.md")

    required_terms = [
        "llm-wiki-core-v0.1.0-mvp.zip",
        "v0.1.0-mvp",
        "git archive",
        "SHA256",
        "exclude .git",
        "exclude generated caches",
    ]
    for term in required_terms:
        assert term in manifest


def test_roadmap_schedule_has_prioritized_follow_up_windows() -> None:
    schedule = _read("docs/roadmap-schedule.md")

    required_terms = [
        "2026-06-26",
        "R0",
        "R1",
        "R2",
        "R3",
        "actual Obsidian CLI read/write/search",
        "URL ingest",
        "batch ingest",
        "deep retrieval",
        "Claude adapter",
    ]
    for term in required_terms:
        assert term in schedule


def test_readme_links_release_process_docs() -> None:
    readme = _read("README.md")

    assert "docs/release-notes-v0.1.0-mvp.md" in readme
    assert "docs/release-notes-v0.4.0-mvp.md" in readme
    assert "docs/archive-manifest.md" in readme
    assert "docs/roadmap-schedule.md" in readme


def test_r4_1_release_notes_capture_user_skill_install_boundary() -> None:
    notes = _read("docs/release-notes-v0.4.0-mvp.md")

    required_terms = [
        "v0.4.0-mvp",
        "R4.1 Codex User-Level Skill Installation",
        "-InstallUserSkill",
        "--install-user-skill",
        "$HOME/.agents/skills/llm-wiki",
        "does not edit global Codex configuration automatically",
        "marketplace-grade Codex plugin publication remains deferred",
        "Claude adapter reconstruction remains deferred",
        "25 passed, 6 skipped",
        "221 passed, 6 skipped",
    ]
    for term in required_terms:
        assert term in notes
