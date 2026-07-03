from __future__ import annotations

import re
from pathlib import Path
import os
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


CLAUDE_PUBLIC_DOCS = [
    "integrations/claude/README.md",
    "integrations/claude/CLAUDE.template.md",
    "integrations/claude/skills/README.md",
    "integrations/claude/skills/llm-wiki/SKILL.md",
    "integrations/claude/commands/wiki.md",
    "integrations/claude/commands/save.md",
]

R4_3_PUBLIC_DOCS = [
    "integrations/claude/README.md",
    "integrations/claude/install/README.md",
    "integrations/claude/skills/README.md",
    "docs/claude-adapter-plan.md",
    "docs/capability-mapping.md",
    "docs/roadmap.md",
    "docs/roadmap-schedule.md",
]

DAMAGED_TEXT_SENTINELS = (
    "\ufffd",
    "闂?,",
    "濞?,",
    "闁?,",
    "闂?,",
    "婵°倗濮撮惌渚€鎯?",
)


def _find_damaged_markers(text: str) -> list[str]:
    return [marker for marker in DAMAGED_TEXT_SENTINELS if marker in text]


def test_r4_3_claude_assets_exist_and_are_project_local() -> None:
    expected = [
        "integrations/claude/CLAUDE.template.md",
        "integrations/claude/skills/README.md",
        "integrations/claude/skills/llm-wiki/SKILL.md",
        "integrations/claude/commands/wiki.md",
        "integrations/claude/commands/save.md",
    ]

    for relative in expected:
        assert (ROOT / relative).is_file(), relative

    readme = _read("integrations/claude/README.md")
    assert "R4.3 local adapter MVP" in readme
    assert "project-local" in readme
    assert "does not edit user-global Claude settings automatically" in readme


def test_claude_skill_frontmatter_and_command_mapping() -> None:
    text = _read("integrations/claude/skills/llm-wiki/SKILL.md")

    assert "name: llm-wiki" in text
    assert "description:" in text
    assert "Claude local adapter MVP" in text
    assert "llm-wiki init <vault> --purpose" in text
    assert "llm-wiki continue <vault>" in text
    assert "llm-wiki detect-transport <vault>" in text
    assert "llm-wiki status <vault>" in text
    assert "llm-wiki ingest <vault> <source>" in text
    assert "llm-wiki ingest-batch <vault> <source-root>" in text
    assert "llm-wiki ingest-url <vault> <url>" in text
    assert "llm-wiki search <vault>" in text
    assert "llm-wiki query <vault>" in text
    assert "llm-wiki save <vault> --title" in text
    assert "llm-wiki lint <vault>" in text
    assert "Do not modify `.raw/` files." in text
    assert "Do not reimplement neutral core file-writing behavior in prompt text." in text


def test_claude_template_documents_llm_wiki_rules() -> None:
    text = _read("integrations/claude/CLAUDE.template.md")

    assert "# LLM Wiki Claude Project Instructions" in text
    assert "Karpathy's LLM Wiki gist is the canonical abstract pattern." in text
    assert "`AgriciDaniel/claude-obsidian` is a reference implementation case" in text
    assert "Use the project-local Claude `llm-wiki` skill" in text
    assert "Raw sources under `.raw/` are immutable." in text
    assert "Artifact-level parity is required." in text
    assert "Byte-for-byte prose parity is not required." in text
    assert "Do not claim full `claude-obsidian` parity." in text


def test_claude_shell_installer_documents_project_local_flags() -> None:
    text = _read("integrations/claude/install/install.sh")

    assert "--install-project-adapter" in text
    assert "--project-destination" in text
    assert "--replace-claude-adapter" in text
    assert ".claude/skills/llm-wiki" in text
    assert ".claude/commands" in text


def test_claude_shell_installer_dry_run_does_not_write_destination(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.sh"
    destination = tmp_path / "target-project"
    destination.mkdir()

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-project-adapter",
            "--project-destination",
            str(destination),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "DRY RUN" in output
    assert "Install Claude project adapter" in output
    assert not (destination / "CLAUDE.md").exists()
    assert not (destination / ".claude").exists()


def test_claude_shell_installer_copies_project_adapter(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.sh"
    destination = tmp_path / "target-project"
    destination.mkdir()

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-project-adapter",
            "--project-destination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Claude project adapter installed" in output
    assert (destination / "CLAUDE.md").exists()
    assert (destination / ".claude" / "skills" / "llm-wiki" / "SKILL.md").exists()
    assert (destination / ".claude" / "commands" / "wiki.md").exists()
    assert (destination / ".claude" / "commands" / "save.md").exists()
    assert not (destination / ".claude" / "settings.json").exists()


def test_claude_shell_installer_refuses_different_existing_claude_md_without_replace(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.sh"
    destination = tmp_path / "target-project"
    destination.mkdir()
    (destination / "CLAUDE.md").write_text("conflicting-contents", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-project-adapter",
            "--project-destination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "--replace-claude-adapter" in output
    assert (destination / "CLAUDE.md").read_text(encoding="utf-8") == "conflicting-contents"
    assert not (destination / ".claude").exists()


def test_claude_shell_installer_replaces_only_adapter_targets_with_flag(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.sh"
    destination = tmp_path / "target-project"
    destination.mkdir()
    (destination / "CLAUDE.md").write_text("conflicting-contents", encoding="utf-8")
    notes = destination / "notes.md"
    notes.write_text("notes-kept", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-project-adapter",
            "--project-destination",
            str(destination),
            "--replace-claude-adapter",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Claude project adapter installed" in output
    assert "LLM Wiki Claude Project Instructions" in (destination / "CLAUDE.md").read_text(encoding="utf-8")
    assert (destination / ".claude" / "skills" / "llm-wiki" / "SKILL.md").exists()
    assert (destination / ".claude" / "commands" / "wiki.md").exists()
    assert (destination / ".claude" / "commands" / "save.md").exists()
    assert notes.read_text(encoding="utf-8") == "notes-kept"
    assert not (destination / ".claude" / "settings.json").exists()


def test_claude_command_wrappers_are_thin() -> None:
    wiki = _read("integrations/claude/commands/wiki.md")
    save = _read("integrations/claude/commands/save.md")

    assert "Read the project-local `llm-wiki` skill" in wiki
    assert "Map `/wiki` intent to neutral `llm-wiki` commands" in wiki
    assert "Do not implement hooks, subagents, or Obsidian-specific automation." in wiki
    assert "Read the project-local `llm-wiki` skill" in save
    assert 'Map `/save` intent to `llm-wiki save <vault> --title "..." --content "..."`.' in save
    assert "Do not save chat noise." in save


def test_r4_3_claude_assets_defer_high_risk_surfaces() -> None:
    combined = "\n".join(_read(relative) for relative in CLAUDE_PUBLIC_DOCS).lower()

    required_deferred = [
        "active claude hooks are deferred",
        "claude subagents are deferred",
        ".claude-plugin packaging is deferred",
        "autoresearch is deferred",
        "canvas workflows are deferred",
        "dragonscale memory is deferred",
        "methodology modes are deferred",
        "automatic git commits are deferred",
    ]
    for phrase in required_deferred:
        assert phrase in combined

    forbidden_claims = [
        "full claude-obsidian parity is complete",
        "active claude hooks are enabled",
        "claude subagents are enabled",
        "autoresearch is implemented",
        "canvas workflows are implemented",
        "dragonscale memory is implemented",
        "automatic git commits are enabled",
    ]
    for phrase in forbidden_claims:
        assert phrase not in combined


def test_r4_3_claude_assets_do_not_ship_active_hooks_subagents_or_plugin() -> None:
    forbidden_paths = [
        "integrations/claude/hooks/hooks.json",
        "integrations/claude/.claude/settings.json",
        "integrations/claude/.claude-plugin/plugin.json",
        "integrations/claude/agents/wiki-ingest.md",
        "integrations/claude/agents/wiki-lint.md",
        "integrations/claude/agents/verifier.md",
    ]

    for relative in forbidden_paths:
        assert not (ROOT / relative).exists(), relative


def test_r4_3_public_docs_have_no_private_paths_or_damaged_text() -> None:
    private_path_patterns = [r"\b[A-Z]:[\\/]", "D:" + "/", "D:" + "\\\\", "C:" + "/", "C:" + "\\\\"]

    for relative in CLAUDE_PUBLIC_DOCS:
        text = _read(relative)
        assert not _find_damaged_markers(text), relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def test_claude_powershell_installer_dry_run_does_not_write_destination(tmp_path) -> None:
    shell = _powershell()
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.ps1"
    destination = tmp_path / "target-project"
    destination.mkdir()

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallProjectAdapter",
            "-ProjectDestination",
            str(destination),
            "-DryRun",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "DRY RUN" in output
    assert "Install Claude project adapter" in output
    assert "CLAUDE.md" in output
    assert ".claude" in output
    assert not (destination / "CLAUDE.md").exists()
    assert not (destination / ".claude").exists()


def test_claude_powershell_installer_copies_project_adapter(tmp_path) -> None:
    shell = _powershell()
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.ps1"
    destination = tmp_path / "target-project"
    destination.mkdir()

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallProjectAdapter",
            "-ProjectDestination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Claude project adapter installed" in output
    assert (destination / "CLAUDE.md").exists()
    assert (destination / ".claude" / "skills" / "llm-wiki" / "SKILL.md").exists()
    assert (destination / ".claude" / "commands" / "wiki.md").exists()
    assert (destination / ".claude" / "commands" / "save.md").exists()
    assert not (destination / ".claude" / "settings.json").exists()
    assert "name: llm-wiki" in (destination / ".claude" / "skills" / "llm-wiki" / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_claude_powershell_installer_refuses_different_existing_files_without_replace(tmp_path) -> None:
    shell = _powershell()
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.ps1"
    destination = tmp_path / "target-project"
    destination.mkdir()
    (destination / "CLAUDE.md").write_text("existing", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallProjectAdapter",
            "-ProjectDestination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "already exists and differs" in output
    assert "ReplaceClaudeAdapter" in output
    assert (destination / "CLAUDE.md").read_text(encoding="utf-8") == "existing"


def test_claude_powershell_installer_replace_updates_only_adapter_targets(tmp_path) -> None:
    shell = _powershell()
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = ROOT / "integrations" / "claude" / "install" / "install.ps1"
    destination = tmp_path / "target-project"
    destination.mkdir()
    (destination / "CLAUDE.md").write_text("existing", encoding="utf-8")
    unrelated = destination / "notes.md"
    unrelated.write_text("keep", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallProjectAdapter",
            "-ProjectDestination",
            str(destination),
            "-ReplaceClaudeAdapter",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Claude project adapter installed" in output
    assert "LLM Wiki Claude Project Instructions" in (destination / "CLAUDE.md").read_text(encoding="utf-8")
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_r4_3_install_docs_describe_project_local_installation() -> None:
    text = _read("integrations/claude/install/README.md")

    assert "# Claude Adapter Install" in text
    assert ".\\install.ps1 -InstallProjectAdapter -ProjectDestination <project> -DryRun" in text
    assert ".\\install.ps1 -InstallProjectAdapter -ProjectDestination <project>" in text
    assert "./install.sh --install-project-adapter --project-destination <project> --dry-run" in text
    assert "./install.sh --install-project-adapter --project-destination <project>" in text
    assert "-ReplaceClaudeAdapter" in text
    assert "--replace-claude-adapter" in text
    assert "does not edit user-global Claude settings automatically" in text
    assert "No active hooks are installed." in text
    assert "No subagents are installed." in text


def test_claude_adapter_plan_records_r4_3_scope_and_deferred_boundaries() -> None:
    text = _read("docs/claude-adapter-plan.md")

    assert "# Claude Adapter Plan" in text
    assert "R4.3 ships a local Claude adapter MVP." in text
    assert "Claude skills are the canonical local adapter surface." in text
    assert "`/wiki` and `/save` are thin command wrappers." in text
    assert "Project-local installation is the default." in text
    assert "Active Claude hooks are deferred." in text
    assert "Claude subagents are deferred." in text
    assert ".claude-plugin packaging is deferred." in text
    assert "Full `claude-obsidian` parity is not claimed." in text


def test_capability_mapping_and_roadmap_record_r4_3() -> None:
    mapping = _read("docs/capability-mapping.md")
    roadmap = _read("docs/roadmap.md")
    schedule = _read("docs/roadmap-schedule.md")

    assert "| Claude local adapter MVP | Claude adapter | R4.3 complete | No Codex dependency | Project-local skill and thin `/wiki` `/save` wrappers | Adapter-only; no hooks or subagents |" in mapping
    assert "R4.3 Claude local adapter MVP is complete for project-local `/wiki` and `/save` usage." in roadmap
    assert "### R4.3: Claude Local Adapter MVP" in schedule
    assert "Status: complete." in schedule
    assert "Project-local `CLAUDE.template.md`." in schedule
    assert "Project-local Claude `llm-wiki` skill." in schedule
    assert "Thin `/wiki` and `/save` wrappers." in schedule
    assert "No active hooks, subagents, `.claude-plugin`, or advanced `claude-obsidian` features." in schedule


def test_r4_3_public_docs_have_no_private_paths_or_damaged_text() -> None:
    damaged = ["\ufffd", "闂?,", "濞?,", "闁?,", "闂?,", "婵°倗濮撮惌渚€鎯?"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", "D:" + "/", "D:" + "\\\\", "C:" + "/", "C:" + "\\\\"]

    for relative in R4_3_PUBLIC_DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"
