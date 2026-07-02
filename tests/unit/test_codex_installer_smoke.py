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


def test_shell_installer_documents_user_skill_install_flags() -> None:
    text = (_repo_root() / "integrations" / "codex" / "install" / "install.sh").read_text(encoding="utf-8")

    assert "--install-user-skill" in text
    assert "--skill-destination" in text
    assert "--replace-user-skill" in text
    assert "$HOME/.agents/skills/llm-wiki" in text


def test_shell_installer_documents_replace_guardrails() -> None:
    text = (_repo_root() / "integrations" / "codex" / "install" / "install.sh").read_text(encoding="utf-8")

    assert "Refusing to replace Codex user skill destination" in text
    assert 'basename "$resolved_skill_destination"' in text
    assert 'case "$resolved_skill_destination" in' in text
    for forbidden in ['""', '|/|.|..|', '"$HOME"', '"$HOME/.agents"', '"$HOME/.agents/skills"', '"llm-wiki"']:
        assert forbidden in text


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


def test_shell_user_skill_install_dry_run_does_not_write_destination(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    destination = tmp_path / "skills" / "llm-wiki"

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-user-skill",
            "--skill-destination",
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
    assert "Install Codex user skill" in output
    assert "llm-wiki" in output
    assert not destination.exists()


def test_shell_user_skill_install_copies_skill_to_destination(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    destination = tmp_path / "skills" / "llm-wiki"

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-user-skill",
            "--skill-destination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Codex user skill installed" in output
    assert (destination / "SKILL.md").exists()


def test_shell_user_skill_install_existing_identical_destination_returns_success(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    source = _repo_root() / "integrations" / "codex" / "skills" / "llm-wiki"
    destination = tmp_path / "skills" / "llm-wiki"
    destination.parent.mkdir(parents=True)
    shutil.copytree(source, destination)

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-user-skill",
            "--skill-destination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "already installed" in output


def test_shell_user_skill_install_refuses_different_existing_destination_without_replace(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    destination = tmp_path / "skills" / "llm-wiki"
    destination.mkdir(parents=True)
    (destination / "SKILL.md").write_text("---\nname: other\n---\n", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-user-skill",
            "--skill-destination",
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "already exists and differs" in output
    assert "--replace-user-skill" in output


def test_shell_user_skill_install_replace_overwrites_existing_destination(tmp_path) -> None:
    if os.name == "nt":
        pytest.skip("POSIX shell execution is checked on non-Windows platforms")

    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("POSIX sh executable is not available")

    script = _repo_root() / "integrations" / "codex" / "install" / "install.sh"
    destination = tmp_path / "skills" / "llm-wiki"
    destination.mkdir(parents=True)
    (destination / "SKILL.md").write_text("---\nname: other\n---\n", encoding="utf-8")
    (destination / "extra.txt").write_text("legacy", encoding="utf-8")

    result = subprocess.run(
        [
            shell,
            str(script),
            "--install-user-skill",
            "--skill-destination",
            str(destination),
            "--replace-user-skill",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Codex user skill installed" in output
    assert (destination / "SKILL.md").exists()
    assert "name: llm-wiki" in (destination / "SKILL.md").read_text(encoding="utf-8")
    assert not (destination / "extra.txt").exists()


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
