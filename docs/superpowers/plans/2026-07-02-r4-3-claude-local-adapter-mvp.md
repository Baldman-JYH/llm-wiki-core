# R4.3 Claude Local Adapter MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local Claude Code adapter MVP that maps `/wiki` and `/save` intent to the neutral `llm-wiki` commands without changing neutral core behavior.

**Architecture:** Keep Claude-specific behavior under `integrations/claude/`. Ship project-local Claude guidance, a canonical `llm-wiki` Claude skill, and thin `/wiki` and `/save` command wrappers that point back to the skill and neutral CLI. Provide conservative project-local install scripts with dry-run, destination override, and explicit replace behavior; do not generate hooks, subagents, plugin packages, or user-global Claude settings.

**Tech Stack:** Markdown adapter assets, PowerShell, POSIX `sh`, Python standard library tests with `pytest`, existing `llm-wiki` CLI commands.

## Global Constraints

- R4.3 must not add runtime dependencies; `pyproject.toml` must keep `dependencies = []`.
- R4.3 must not change neutral core operation behavior.
- R4.3 must not implement active Claude hooks.
- R4.3 must not implement Claude subagents.
- R4.3 must not implement `.claude-plugin` packaging.
- R4.3 must not implement marketplace publishing.
- R4.3 must not mutate user-global Claude configuration automatically.
- R4.3 must not write to user-level `~/.claude` by default.
- R4.3 must not implement `autoresearch`, canvas workflows, hybrid retrieval, vector search, reranking, qmd integration, DragonScale memory, methodology modes, automatic Git commits, Obsidian-specific setup, remote Codex Web, or remote Claude Web.
- R4.3 must use artifact-level parity, not byte-for-byte prose parity.
- R4.3 must not claim full `claude-obsidian` parity.
- Windows support must use native PowerShell and must not require WSL or Git Bash.
- macOS and Linux support should use POSIX shell.
- Public docs and tests must avoid private local absolute paths and damaged text.
- Commit messages must be written in Chinese.

---

## File Structure

- Create `integrations/claude/CLAUDE.template.md`: project-level Claude instructions for the LLM Wiki workflow.
- Create `integrations/claude/skills/llm-wiki/SKILL.md`: canonical Claude skill instructions for local `llm-wiki` usage.
- Create `integrations/claude/skills/README.md`: explain the Claude skill surface and project-local destination.
- Create `integrations/claude/commands/wiki.md`: thin `/wiki` wrapper that tells Claude to use the `llm-wiki` skill and neutral commands.
- Create `integrations/claude/commands/save.md`: thin `/save` wrapper that tells Claude to use the `llm-wiki` skill and neutral save command.
- Create `integrations/claude/install/install.ps1`: PowerShell project-local adapter installer.
- Create `integrations/claude/install/install.sh`: POSIX project-local adapter installer.
- Create `integrations/claude/install/README.md`: installation and verification guide.
- Modify `integrations/claude/README.md`: document R4.3 assets, install surface, and deferred boundaries.
- Create `docs/claude-adapter-plan.md`: public adapter plan for R4.3 and future Claude work.
- Modify `docs/capability-mapping.md`: mark Claude local adapter MVP as R4.3.
- Modify `docs/roadmap.md`: record R4.3 local Claude adapter MVP.
- Modify `docs/roadmap-schedule.md`: add R4.3 schedule entry.
- Create `tests/unit/test_r4_3_claude_adapter_assets.py`: guard Claude assets, installers, docs, and deferred boundaries.
- Modify external `../codex_doc/project_understanding_progress.md`: record stage progress outside the repository.
- Do not modify `src/llm_wiki/` or other neutral core operation files.

---

### Task 1: Claude Adapter Assets And Guard Tests

**Files:**
- Create: `tests/unit/test_r4_3_claude_adapter_assets.py`
- Create: `integrations/claude/CLAUDE.template.md`
- Create: `integrations/claude/skills/llm-wiki/SKILL.md`
- Create: `integrations/claude/skills/README.md`
- Create: `integrations/claude/commands/wiki.md`
- Create: `integrations/claude/commands/save.md`
- Modify: `integrations/claude/README.md`

**Interfaces:**
- Consumes: R4.3 spec at `docs/superpowers/specs/2026-07-02-r4-3-claude-local-adapter-mvp-design.md`
- Produces: Claude adapter assets that Tasks 2 and 3 installers copy into a target project

- [ ] **Step 1: Write failing Claude adapter asset tests**

Create `tests/unit/test_r4_3_claude_adapter_assets.py`:

```python
from __future__ import annotations

import re
from pathlib import Path


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


def test_claude_command_wrappers_are_thin() -> None:
    wiki = _read("integrations/claude/commands/wiki.md")
    save = _read("integrations/claude/commands/save.md")

    assert "Read the project-local `llm-wiki` skill" in wiki
    assert "Map `/wiki` intent to neutral `llm-wiki` commands" in wiki
    assert "Do not implement hooks, subagents, or Obsidian-specific automation." in wiki
    assert "Read the project-local `llm-wiki` skill" in save
    assert "Map `/save` intent to `llm-wiki save <vault> --title" in save
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


def test_r4_3_claude_public_docs_have_no_private_paths_or_damaged_text() -> None:
    damaged = ["\ufffd", "闁", "娑", "閻", "闂", "濡ょ姴鐭侀惁"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", "D:" + "/", "D:" + r"\\", "C:" + "/", "C:" + r"\\"]

    for relative in CLAUDE_PUBLIC_DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"
```

- [ ] **Step 2: Run asset tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py -q
```

Expected: fail because R4.3 Claude adapter assets do not exist yet.

- [ ] **Step 3: Create `CLAUDE.template.md`**

Create `integrations/claude/CLAUDE.template.md`:

```markdown
# LLM Wiki Claude Project Instructions

Karpathy's LLM Wiki gist is the canonical abstract pattern.

`AgriciDaniel/claude-obsidian` is a reference implementation case, not the canonical abstraction.

Use the project-local Claude `llm-wiki` skill for wiki work.

## Core Rules

- Raw sources under `.raw/` are immutable.
- Generated Markdown wiki pages are durable artifacts.
- Artifact-level parity is required.
- Byte-for-byte prose parity is not required.
- Do not claim full `claude-obsidian` parity.
- Do not modify `.raw/` files.
- Do not edit user-global Claude settings.

## Command Policy

Map wiki work to neutral `llm-wiki` commands:

- setup or new wiki: `llm-wiki init <vault> --purpose "..."`
- continue: `llm-wiki continue <vault>`
- transport check: `llm-wiki detect-transport <vault>`
- status: `llm-wiki status <vault>`
- ingest one source: `llm-wiki ingest <vault> <source>`
- ingest folder: `llm-wiki ingest-batch <vault> <source-root>`
- ingest URL: `llm-wiki ingest-url <vault> <url>`
- search: `llm-wiki search <vault> "<query>"`
- query: `llm-wiki query <vault> "<question>"`
- save: `llm-wiki save <vault> --title "..." --content "..."`
- lint: `llm-wiki lint <vault>`

## Deferred Surfaces

Active Claude hooks are deferred.

Claude subagents are deferred.

`.claude-plugin` packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.
```

- [ ] **Step 4: Create Claude skill and command wrappers**

Create `integrations/claude/skills/llm-wiki/SKILL.md`:

```markdown
---
name: llm-wiki
description: Claude local adapter MVP for maintaining a durable Markdown LLM Wiki through neutral llm-wiki commands.
---

# LLM Wiki Claude Skill

Claude local adapter MVP for `llm-wiki-core`.

Use this skill when the user asks to set up, continue, ingest, search, query, save, or lint an LLM Wiki.

## Source Of Truth

Karpathy's LLM Wiki gist is the canonical abstract pattern.

`AgriciDaniel/claude-obsidian` is a reference implementation case.

## Non-Negotiable Rules

- Do not modify `.raw/` files.
- Do not reimplement neutral core file-writing behavior in prompt text.
- Do not claim full `claude-obsidian` parity.
- Do not enable active hooks.
- Do not use Claude subagents.
- Do not edit user-global Claude settings.

## Command Mapping

Use these neutral commands:

- `/wiki` on a new vault: `llm-wiki init <vault> --purpose "..."`
- `/wiki` on an existing vault: `llm-wiki continue <vault>`
- `/wiki transport`: `llm-wiki detect-transport <vault>`
- `/wiki status`: `llm-wiki status <vault>`
- `/wiki ingest <source>`: `llm-wiki ingest <vault> <source>`
- `/wiki ingest-batch <source-root>`: `llm-wiki ingest-batch <vault> <source-root>`
- `/wiki ingest-url <url>`: `llm-wiki ingest-url <vault> <url>`
- `/wiki search <query>`: `llm-wiki search <vault> "<query>"`
- `/wiki query <question>`: `llm-wiki query <vault> "<question>"`
- `/save`: `llm-wiki save <vault> --title "..." --content "..."`
- `/wiki lint`: `llm-wiki lint <vault>`

## Deferred In R4.3

Active Claude hooks are deferred.

Claude subagents are deferred.

`.claude-plugin` packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.
```

Create `integrations/claude/commands/wiki.md`:

```markdown
---
description: Thin /wiki wrapper for the project-local llm-wiki Claude skill.
---

Read the project-local `llm-wiki` skill.

Map `/wiki` intent to neutral `llm-wiki` commands.

Use `/wiki` on a new vault for `llm-wiki init <vault> --purpose "..."`.

Use `/wiki` on an existing vault for `llm-wiki continue <vault>`.

Use explicit subcommands for transport, status, ingest, ingest-batch, ingest-url, search, query, and lint.

Do not implement hooks, subagents, or Obsidian-specific automation.
```

Create `integrations/claude/commands/save.md`:

```markdown
---
description: Thin /save wrapper for saving durable LLM Wiki knowledge.
---

Read the project-local `llm-wiki` skill.

Map `/save` intent to `llm-wiki save <vault> --title "..." --content "..."`.

Save durable knowledge, decisions, concepts, or session summaries.

Do not save chat noise.

Do not modify `.raw/` files.
```

- [ ] **Step 5: Create Claude skills README and update adapter README**

Create `integrations/claude/skills/README.md`:

```markdown
# Claude Skills

The canonical R4.3 Claude local adapter surface is the `llm-wiki` skill.

Install it project-locally under:

```text
.claude/skills/llm-wiki/SKILL.md
```

The `/wiki` and `/save` command wrappers are thin entry points that tell Claude to read this skill and use neutral `llm-wiki` commands.

Active Claude hooks are deferred.

Claude subagents are deferred.

`.claude-plugin` packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.
```

Update `integrations/claude/README.md` so it includes:

```markdown
## R4.3 Local Adapter MVP

R4.3 local adapter MVP provides project-local Claude assets for `/wiki` and `/save`.

It is project-local and does not edit user-global Claude settings automatically.

Canonical surface:

- `CLAUDE.template.md`
- `skills/llm-wiki/SKILL.md`
- thin `commands/wiki.md` and `commands/save.md` wrappers

Active Claude hooks are deferred.

Claude subagents are deferred.

`.claude-plugin` packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.
```

Keep the existing R4.2 command mapping and neutral core boundary wording.

- [ ] **Step 6: Run focused asset tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py -q
```

Expected: `7 passed`.

- [ ] **Step 7: Commit Task 1**

Run:

```powershell
git add tests/unit/test_r4_3_claude_adapter_assets.py integrations/claude/CLAUDE.template.md integrations/claude/skills/llm-wiki/SKILL.md integrations/claude/skills/README.md integrations/claude/commands/wiki.md integrations/claude/commands/save.md integrations/claude/README.md
git commit -m "添加 R4.3 Claude 本地适配器资产"
```

---

### Task 2: PowerShell Project-Local Claude Adapter Installer

**Files:**
- Modify: `tests/unit/test_r4_3_claude_adapter_assets.py`
- Create: `integrations/claude/install/install.ps1`

**Interfaces:**
- Consumes: Claude adapter assets from Task 1
- Produces: PowerShell flags `-InstallProjectAdapter`, `-ProjectDestination <path>`, `-DryRun`, and `-ReplaceClaudeAdapter`

- [ ] **Step 1: Add failing PowerShell installer tests**

Append to `tests/unit/test_r4_3_claude_adapter_assets.py`:

```python
import shutil
import subprocess

import pytest


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
    assert "name: llm-wiki" in (destination / ".claude" / "skills" / "llm-wiki" / "SKILL.md").read_text(encoding="utf-8")


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
```

- [ ] **Step 2: Run PowerShell installer tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_dry_run_does_not_write_destination tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_copies_project_adapter tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_refuses_different_existing_files_without_replace tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_replace_updates_only_adapter_targets -q
```

Expected: fail because `integrations/claude/install/install.ps1` does not exist.

- [ ] **Step 3: Implement PowerShell installer**

Create `integrations/claude/install/install.ps1`:

```powershell
param(
  [switch]$InstallProjectAdapter,
  [string]$ProjectDestination,
  [switch]$DryRun,
  [switch]$ReplaceClaudeAdapter
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")
$ClaudeSource = Join-Path $RepoRoot "integrations\claude"

function Test-RequiredFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Claude adapter source file not found at `"$Path`"."
  }
}

function Test-FileIdentical {
  param([string]$Source, [string]$Destination)
  if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
    return $false
  }
  return (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
}

function Copy-AdapterFile {
  param([string]$Source, [string]$Destination)

  Test-RequiredFile -Path $Source

  if ($DryRun) {
    Write-Host "DRY RUN: Copy `"$Source`" to `"$Destination`""
    return
  }

  if (Test-Path -LiteralPath $Destination) {
    if (Test-FileIdentical -Source $Source -Destination $Destination) {
      return
    }
    if (-not $ReplaceClaudeAdapter) {
      throw "Claude adapter destination already exists and differs. Re-run with -ReplaceClaudeAdapter to replace it."
    }
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
      throw "Claude adapter destination already exists and differs. Re-run with -ReplaceClaudeAdapter to replace it."
    }
    Remove-Item -LiteralPath $Destination -Force
  }

  $parent = Split-Path -Parent $Destination
  if (-not [string]::IsNullOrWhiteSpace($parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
  Copy-Item -LiteralPath $Source -Destination $Destination
}

function Install-ProjectAdapter {
  if ([string]::IsNullOrWhiteSpace($ProjectDestination)) {
    throw "Claude project adapter install requires -ProjectDestination."
  }

  if (-not (Test-Path -LiteralPath $ProjectDestination -PathType Container)) {
    throw "Claude project adapter destination must be an existing directory."
  }

  $resolvedProject = (Resolve-Path -LiteralPath $ProjectDestination).Path
  Write-Host "Install Claude project adapter into `"$resolvedProject`""

  $targets = @(
    @{ Source = Join-Path $ClaudeSource "CLAUDE.template.md"; Destination = Join-Path $resolvedProject "CLAUDE.md" },
    @{ Source = Join-Path $ClaudeSource "skills\llm-wiki\SKILL.md"; Destination = Join-Path $resolvedProject ".claude\skills\llm-wiki\SKILL.md" },
    @{ Source = Join-Path $ClaudeSource "commands\wiki.md"; Destination = Join-Path $resolvedProject ".claude\commands\wiki.md" },
    @{ Source = Join-Path $ClaudeSource "commands\save.md"; Destination = Join-Path $resolvedProject ".claude\commands\save.md" }
  )

  foreach ($target in $targets) {
    Copy-AdapterFile -Source $target.Source -Destination $target.Destination
  }

  if ($DryRun) {
    return
  }

  Write-Host "Claude project adapter installed at `"$resolvedProject`""
  Write-Host "Next Claude prompt: /wiki status"
  Write-Host "Next Claude prompt: /save"
}

if (-not $InstallProjectAdapter) {
  throw "Use -InstallProjectAdapter to install the Claude project adapter."
}

Install-ProjectAdapter
```

- [ ] **Step 4: Run focused PowerShell installer tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_dry_run_does_not_write_destination tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_copies_project_adapter tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_refuses_different_existing_files_without_replace tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_powershell_installer_replace_updates_only_adapter_targets -q
```

Expected: `4 passed` on Windows with PowerShell available.

- [ ] **Step 5: Commit Task 2**

Run:

```powershell
git add tests/unit/test_r4_3_claude_adapter_assets.py integrations/claude/install/install.ps1
git commit -m "实现 R4.3 Claude PowerShell 本地安装"
```

---

### Task 3: POSIX Project-Local Claude Adapter Installer

**Files:**
- Modify: `tests/unit/test_r4_3_claude_adapter_assets.py`
- Create: `integrations/claude/install/install.sh`

**Interfaces:**
- Consumes: Claude adapter assets from Task 1
- Produces: shell flags `--install-project-adapter`, `--project-destination PATH`, `--dry-run`, and `--replace-claude-adapter`

- [ ] **Step 1: Add failing shell installer tests**

Append to `tests/unit/test_r4_3_claude_adapter_assets.py`:

```python
import os


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
```

- [ ] **Step 2: Run shell installer tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_shell_installer_documents_project_local_flags tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_shell_installer_dry_run_does_not_write_destination tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_shell_installer_copies_project_adapter -q
```

Expected on Windows: static test fails because the script does not exist; runtime tests skip.

- [ ] **Step 3: Implement POSIX installer**

Create `integrations/claude/install/install.sh`:

```sh
#!/usr/bin/env sh
set -eu

DRY_RUN=0
INSTALL_PROJECT_ADAPTER=0
REPLACE_CLAUDE_ADAPTER=0
PROJECT_DESTINATION=""

usage() {
  echo "Usage: install.sh --install-project-adapter --project-destination PATH [--dry-run] [--replace-claude-adapter]" >&2
}

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"
CLAUDE_SOURCE="$REPO_ROOT/integrations/claude"

copy_adapter_file() {
  source_file="$1"
  destination_file="$2"

  if [ ! -f "$source_file" ]; then
    echo "Claude adapter source file not found at \"$source_file\"." >&2
    exit 1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY RUN: Copy \"$source_file\" to \"$destination_file\""
    return 0
  fi

  if [ -e "$destination_file" ]; then
    if [ -f "$destination_file" ] && cmp -s "$source_file" "$destination_file"; then
      return 0
    fi
    if [ "$REPLACE_CLAUDE_ADAPTER" -ne 1 ]; then
      echo "Claude adapter destination already exists and differs. Re-run with --replace-claude-adapter to replace it." >&2
      exit 1
    fi
    if [ ! -f "$destination_file" ]; then
      echo "Claude adapter destination already exists and differs. Re-run with --replace-claude-adapter to replace it." >&2
      exit 1
    fi
    rm -f "$destination_file"
  fi

  destination_parent="$(dirname "$destination_file")"
  mkdir -p "$destination_parent"
  cp "$source_file" "$destination_file"
}

install_project_adapter() {
  if [ -z "$PROJECT_DESTINATION" ]; then
    echo "Claude project adapter install requires --project-destination PATH." >&2
    exit 2
  fi

  if [ ! -d "$PROJECT_DESTINATION" ]; then
    echo "Claude project adapter destination must be an existing directory." >&2
    exit 1
  fi

  echo "Install Claude project adapter into \"$PROJECT_DESTINATION\""

  copy_adapter_file "$CLAUDE_SOURCE/CLAUDE.template.md" "$PROJECT_DESTINATION/CLAUDE.md"
  copy_adapter_file "$CLAUDE_SOURCE/skills/llm-wiki/SKILL.md" "$PROJECT_DESTINATION/.claude/skills/llm-wiki/SKILL.md"
  copy_adapter_file "$CLAUDE_SOURCE/commands/wiki.md" "$PROJECT_DESTINATION/.claude/commands/wiki.md"
  copy_adapter_file "$CLAUDE_SOURCE/commands/save.md" "$PROJECT_DESTINATION/.claude/commands/save.md"

  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi

  echo "Claude project adapter installed at \"$PROJECT_DESTINATION\""
  echo "Next Claude prompt: /wiki status"
  echo "Next Claude prompt: /save"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --install-project-adapter)
      INSTALL_PROJECT_ADAPTER=1
      shift
      ;;
    --project-destination)
      if [ "$#" -lt 2 ]; then
        usage
        exit 2
      fi
      PROJECT_DESTINATION="$2"
      shift 2
      ;;
    --replace-claude-adapter)
      REPLACE_CLAUDE_ADAPTER=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

if [ "$INSTALL_PROJECT_ADAPTER" -ne 1 ]; then
  usage
  exit 2
fi

install_project_adapter
```

- [ ] **Step 4: Run installer tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py -q
```

Expected on Windows: PowerShell tests pass and POSIX runtime tests skip.

- [ ] **Step 5: Commit Task 3**

Run:

```powershell
git add tests/unit/test_r4_3_claude_adapter_assets.py integrations/claude/install/install.sh
git commit -m "实现 R4.3 Claude Shell 本地安装"
```

---

### Task 4: R4.3 Documentation And Roadmap Guardrails

**Files:**
- Modify: `tests/unit/test_r4_3_claude_adapter_assets.py`
- Create: `integrations/claude/install/README.md`
- Create: `docs/claude-adapter-plan.md`
- Modify: `docs/capability-mapping.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/roadmap-schedule.md`

**Interfaces:**
- Consumes: assets and installer flags from Tasks 1, 2, and 3
- Produces: public documentation and roadmap state for R4.3

- [ ] **Step 1: Add failing docs and roadmap tests**

Append to `tests/unit/test_r4_3_claude_adapter_assets.py`:

```python
R4_3_PUBLIC_DOCS = [
    "integrations/claude/README.md",
    "integrations/claude/install/README.md",
    "integrations/claude/skills/README.md",
    "docs/claude-adapter-plan.md",
    "docs/capability-mapping.md",
    "docs/roadmap.md",
    "docs/roadmap-schedule.md",
]


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
    damaged = ["\ufffd", "闁", "娑", "閻", "闂", "濡ょ姴鐭侀惁"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", "D:" + "/", "D:" + r"\\", "C:" + "/", "C:" + r"\\"]

    for relative in R4_3_PUBLIC_DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"
```

- [ ] **Step 2: Run docs tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py::test_r4_3_install_docs_describe_project_local_installation tests/unit/test_r4_3_claude_adapter_assets.py::test_claude_adapter_plan_records_r4_3_scope_and_deferred_boundaries tests/unit/test_r4_3_claude_adapter_assets.py::test_capability_mapping_and_roadmap_record_r4_3 tests/unit/test_r4_3_claude_adapter_assets.py::test_r4_3_public_docs_have_no_private_paths_or_damaged_text -q
```

Expected: fail because install docs and public plan do not exist and roadmap is not updated.

- [ ] **Step 3: Create install README**

Create `integrations/claude/install/README.md`:

```markdown
# Claude Adapter Install

R4.3 installs Claude adapter assets into a project-local destination.

It does not edit user-global Claude settings automatically.

## PowerShell

```powershell
.\install.ps1 -InstallProjectAdapter -ProjectDestination <project> -DryRun
.\install.ps1 -InstallProjectAdapter -ProjectDestination <project>
.\install.ps1 -InstallProjectAdapter -ProjectDestination <project> -ReplaceClaudeAdapter
```

## POSIX Shell

```sh
./install.sh --install-project-adapter --project-destination <project> --dry-run
./install.sh --install-project-adapter --project-destination <project>
./install.sh --install-project-adapter --project-destination <project> --replace-claude-adapter
```

## Installed Files

- `CLAUDE.md`
- `.claude/skills/llm-wiki/SKILL.md`
- `.claude/commands/wiki.md`
- `.claude/commands/save.md`

No active hooks are installed.

No subagents are installed.

No `.claude/settings.json` file is generated.

No user-global `~/.claude` files are modified.

## Verification

Start Claude Code in the target project and try:

- `/wiki status`
- `/wiki search durable knowledge`
- `/save`
```

- [ ] **Step 4: Create public Claude adapter plan**

Create `docs/claude-adapter-plan.md`:

```markdown
# Claude Adapter Plan

R4.3 ships a local Claude adapter MVP.

Claude skills are the canonical local adapter surface.

`/wiki` and `/save` are thin command wrappers.

Project-local installation is the default.

## R4.3 Scope

- project-local `CLAUDE.template.md`;
- project-local Claude `llm-wiki` skill;
- thin `/wiki` command wrapper;
- thin `/save` command wrapper;
- PowerShell and POSIX project-local install scripts;
- guard tests for deferred boundaries.

## Deferred

Active Claude hooks are deferred.

Claude subagents are deferred.

`.claude-plugin` packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.

Full `claude-obsidian` parity is not claimed.
```

- [ ] **Step 5: Update capability mapping and roadmap docs**

In `docs/capability-mapping.md`, add this row after `Claude schema guidance`:

```markdown
| Claude local adapter MVP | Claude adapter | R4.3 complete | No Codex dependency | Project-local skill and thin `/wiki` `/save` wrappers | Adapter-only; no hooks or subagents |
```

In `docs/roadmap.md`, add:

```markdown
R4.3 Claude local adapter MVP is complete for project-local `/wiki` and `/save` usage.
```

In `docs/roadmap-schedule.md`, set the R4 status line to:

```markdown
Status: R4.3 complete; remaining R4.x advanced adapter work deferred.
```

Add this section after R4.2:

```markdown
### R4.3: Claude Local Adapter MVP

Window: 2026-07-02

Status: complete.

Scope:

- Project-local `CLAUDE.template.md`.
- Project-local Claude `llm-wiki` skill.
- Thin `/wiki` and `/save` wrappers.
- PowerShell and POSIX project-local install scripts.
- Guard tests for no active hooks, subagents, `.claude-plugin`, or advanced `claude-obsidian` features.

Completed outcome:

- Claude Code users can install project-local adapter assets.
- `/wiki` and `/save` intent maps to neutral `llm-wiki` commands.
- User-global Claude settings are not edited automatically.
- No active hooks, subagents, `.claude-plugin`, or advanced `claude-obsidian` features are shipped.

Non-scope:

- Active Claude hooks.
- Claude subagents.
- `.claude-plugin` packaging.
- Autoresearch, canvas, hybrid retrieval, DragonScale, methodology modes, and automatic Git commits.

Exit criteria:

- Claude local adapter assets are public, tested, project-local, and limited to artifact-level parity.
```

- [ ] **Step 6: Run focused and adjacent docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_0_adapter_packaging_docs.py -q
```

Expected: R4.3, R4.2, and R4.0 docs tests pass; POSIX runtime skips are not part of this command.

- [ ] **Step 7: Commit Task 4**

Run:

```powershell
git add tests/unit/test_r4_3_claude_adapter_assets.py integrations/claude/install/README.md docs/claude-adapter-plan.md docs/capability-mapping.md docs/roadmap.md docs/roadmap-schedule.md
git commit -m "补充 R4.3 Claude 适配器文档与路线图"
```

---

### Task 5: Final R4.3 Verification And Progress Record

**Files:**
- Modify: external `../codex_doc/project_understanding_progress.md`
- No repository code changes unless verification exposes a defect.

**Interfaces:**
- Consumes: R4.3 task commits.
- Produces: verified branch state and external progress record.

- [ ] **Step 1: Run focused R4.3 tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py -q
```

Expected: all R4.3 tests pass, with POSIX runtime skips allowed on Windows.

- [ ] **Step 2: Run adjacent adapter tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_integration_skeleton.py -q
```

Expected: all adjacent tests pass.

- [ ] **Step 3: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with existing platform skips allowed.

- [ ] **Step 4: Run whitespace checks**

Run:

```powershell
git diff --check
$base = git merge-base main HEAD
git diff --check "$base..HEAD"
```

Expected: no whitespace errors.

- [ ] **Step 5: Confirm dependency boundary**

Run:

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies = \[\]"
```

Expected output includes:

```text
dependencies = []
```

- [ ] **Step 6: Confirm branch status and recent commits**

Run:

```powershell
git status --short --branch
git log --oneline -8
```

Expected:

- branch is `r4-3-claude-local-adapter-mvp-design`;
- working tree is clean before final review;
- recent R4.3 commits use Chinese commit messages.

- [ ] **Step 7: Update external progress document**

Append a stage to external `../codex_doc/project_understanding_progress.md` recording:

```markdown
## 阶段 136：R4.3 Claude Local Adapter MVP 实现完成

- 分支：`r4-3-claude-local-adapter-mvp-design`
- 任务：完成 R4.3 Claude local adapter MVP assets、project-local installers、docs、roadmap 与 guard tests。
- 提交：记录本阶段 R4.3 implementation commits。
- 结果：Claude adapter 提供 project-local `CLAUDE.template.md`、`llm-wiki` skill、thin `/wiki` `/save` wrappers、PowerShell/POSIX install scripts；所有 Claude surfaces 映射到 neutral `llm-wiki` commands。
- 边界：active Claude hooks、Claude subagents、`.claude-plugin`、autoresearch、canvas、hybrid retrieval、DragonScale、methodology modes、automatic Git commits、Obsidian-specific setup、remote Codex/Claude Web 均仍 deferred。
- 验证：记录 focused R4.3 tests、adjacent adapter tests、full suite、`git diff --check`、range-based whitespace check、`pyproject.toml dependencies = []` 的实际结果。
```

- [ ] **Step 8: Report final R4.3 status**

Report:

- branch name;
- latest commit hash;
- focused R4.3 test result;
- adjacent adapter test result;
- full suite result;
- whitespace check result;
- dependency boundary result;
- reminder that R4.3 is a local Claude adapter MVP, not full `claude-obsidian` parity.
