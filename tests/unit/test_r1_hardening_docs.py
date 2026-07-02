from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_r1_hardening_report_documents_completed_scope() -> None:
    report = _read("docs/r1-hardening-report.md")

    required_terms = [
        "# R1 Hardening Report",
        "Status: complete",
        "CLI JSON output",
        "frontmatter-field",
        ".raw/ path errors",
        "post-MVP",
    ]
    for term in required_terms:
        assert term in report


def test_readme_documents_machine_readable_cli_output() -> None:
    readme = _read("README.md")

    assert "--json" in readme
    assert "machine-readable JSON" in readme


def test_user_guide_uses_generic_paths_and_documents_json_output() -> None:
    guide = _read("docs/user-guide.md")

    forbidden_fragments = [
        "D:\\ai",
        "D:/ai",
        "D:\\path\\to\\vault",
        "D:/path/to/vault",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in guide

    assert "llm-wiki status <vault> --json" in guide
    assert '"status": "error"' in guide


def test_roadmap_schedule_marks_r1_complete() -> None:
    schedule = _read("docs/roadmap-schedule.md")

    assert "## R1: Hardening" in schedule
    assert "Status: complete." in schedule
    assert "Optional machine-readable CLI output." in schedule


def test_release_notes_preserve_mvp_boundary_for_r1() -> None:
    notes = _read("docs/release-notes-v0.1.0-mvp.md")

    assert "## Post-MVP R1 Hardening" in notes
    assert "does not move the `v0.1.0-mvp` tag" in notes
