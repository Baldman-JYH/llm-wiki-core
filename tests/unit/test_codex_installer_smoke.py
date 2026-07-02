from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess

import pytest


def _repo_root() -> Path:
    return Path(__file__).parents[2]


def test_powershell_installer_has_dry_run_plan_and_reentry_hints() -> None:
    script = _repo_root() / "integrations" / "codex" / "install" / "install.ps1"
    text = script.read_text(encoding="utf-8")

    assert "DryRun" in text
    assert "pip install -e" in text
    assert "llm-wiki init" in text
    assert "llm-wiki detect-transport" in text
    assert "llm-wiki status" in text
    assert "llm-wiki continue" in text


def test_shell_installer_has_dry_run_plan_and_reentry_hints() -> None:
    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    text = script.read_text(encoding="utf-8")

    assert "--dry-run" in text
    assert "pip install -e" in text
    assert "llm-wiki init" in text
    assert "llm-wiki detect-transport" in text
    assert "llm-wiki status" in text
    assert "llm-wiki continue" in text


def test_install_readme_uses_portable_examples_not_private_paths() -> None:
    text = (_repo_root() / "integrations" / "codex" / "install" / "README.md").read_text(encoding="utf-8")

    assert "<vault>" in text
    assert "D:\\path\\to\\vault" not in text
    assert "/path/to/vault" not in text
    assert "WSL" not in text
    assert "Git Bash" not in text


def test_powershell_installer_dry_run_does_not_create_vault(tmp_path) -> None:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.ps1"
    vault = tmp_path / "dry run vault"

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-VaultPath",
            str(vault),
            "-Purpose",
            "Installer dry run",
            "-DryRun",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "DRY RUN" in output
    assert "pip install -e" in output
    assert "llm-wiki init" in output
    assert "llm-wiki detect-transport" in output
    assert "llm-wiki status" in output
    assert "llm-wiki continue" in output
    assert not vault.exists()


def test_shell_installer_dry_run_does_not_create_vault(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell dry-run execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    vault = tmp_path / "dry run vault"

    result = subprocess.run(
        [shell, str(script), "--dry-run", str(vault), "Installer dry run"],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "DRY RUN" in output
    assert "pip install -e" in output
    assert "llm-wiki init" in output
    assert "llm-wiki detect-transport" in output
    assert "llm-wiki status" in output
    assert "llm-wiki continue" in output
    assert not vault.exists()


def test_powershell_user_skill_install_dry_run_does_not_write_destination(tmp_path) -> None:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.ps1"
    destination = tmp_path / "skills" / "llm-wiki"

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallUserSkill",
            "-SkillDestination",
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
    assert "Install Codex user skill" in output
    assert "integrations" in output
    assert "llm-wiki" in output
    assert not destination.exists()


def test_powershell_user_skill_install_copies_skill_to_destination(tmp_path) -> None:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.ps1"
    destination = tmp_path / "skills" / "llm-wiki"

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallUserSkill",
            "-SkillDestination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Codex user skill installed" in output
    skill = destination / "SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert "name: llm-wiki" in text
    assert "llm-wiki search" in text


def test_powershell_user_skill_install_refuses_different_existing_destination(tmp_path) -> None:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("PowerShell executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.ps1"
    destination = tmp_path / "skills" / "llm-wiki"
    destination.mkdir(parents=True)
    (destination / "SKILL.md").write_text("---\nname: other\n---\n", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-InstallUserSkill",
            "-SkillDestination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "already exists and differs" in output
    assert "ReplaceUserSkill" in output
