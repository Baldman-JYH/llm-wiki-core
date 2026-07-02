from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


DOCS = [
    "integrations/codex/install/README.md",
    "integrations/codex/README.md",
    "integrations/codex/skills/README.md",
    "docs/adapter-packaging-plan.md",
    "docs/roadmap-schedule.md",
]

PROCESS_DOCS = [
    "docs/superpowers/plans/2026-07-02-r4-1-codex-user-skill-installation.md",
    "docs/superpowers/specs/2026-07-02-r4-1-codex-user-skill-installation-design.md",
]


def test_r4_1_docs_have_no_private_paths_or_damaged_text() -> None:
    damaged = ["\ufffd", "闂?", "濞?", "闁?", "婵°倗濮撮惌渚€鎯?"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\"]

    for relative in DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"


def test_r4_1_process_docs_have_no_private_workspace_paths() -> None:
    private_workspace_markers = [
        "D:/ai/llmWiki",
        "D:\\ai\\llmWiki",
        "C:/Users/Administrator",
        "C:\\Users\\Administrator",
    ]

    for relative in PROCESS_DOCS:
        text = _read(relative)
        assert not [marker for marker in private_workspace_markers if marker in text], relative


def test_install_readme_documents_explicit_user_skill_install() -> None:
    text = _read("integrations/codex/install/README.md")

    assert ".\\install.ps1 -InstallUserSkill -DryRun" in text
    assert ".\\install.ps1 -InstallUserSkill" in text
    assert "./install.sh --install-user-skill --dry-run" in text
    assert "./install.sh --install-user-skill" in text
    assert "$HOME/.agents/skills/llm-wiki" in text
    assert "does not edit global Codex configuration automatically" in text
    assert (
        "Use `-SkillDestination <path>` or `--skill-destination <path>` for tests or advanced installs."
        in text
    )


def test_codex_adapter_docs_state_user_skill_mode_is_explicit_and_verifiable() -> None:
    readme = _read("integrations/codex/README.md")
    skills = _read("integrations/codex/skills/README.md")

    assert "User-level skill installation is explicit" in readme
    assert "dry-run capable" in readme
    assert "Start a new Codex session after installing the skill." in readme
    assert "$HOME/.agents/skills/llm-wiki" in skills
    assert "Verify `SKILL.md` contains `name: llm-wiki`" in skills
    assert "check wiki status" in skills
    assert "search wiki for durable knowledge" in skills


def test_r4_1_roadmap_and_packaging_plan_boundaries() -> None:
    packaging = _read("docs/adapter-packaging-plan.md")
    schedule = _read("docs/roadmap-schedule.md")

    assert "R4.1 adds explicit user-level skill installation." in packaging
    assert "R4.1 does not publish a marketplace-grade Codex plugin." in packaging
    assert "R4.1 does not edit global Codex configuration automatically." in packaging
    assert "### R4.1: Codex User-Level Skill Installation" in schedule
    assert "Status: complete." in schedule
    assert "Release: `v0.4.0-mvp`." in schedule
    assert "Explicit `-InstallUserSkill` and `--install-user-skill` paths." in schedule
