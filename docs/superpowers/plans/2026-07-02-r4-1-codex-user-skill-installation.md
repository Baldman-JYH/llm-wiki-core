# R4.1 Codex User-Level Skill Installation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit, dry-run-capable Codex user-level skill installation path without changing neutral core behavior.

**Architecture:** Keep repo-local install as the baseline. Extend the existing Codex install scripts with explicit user-level skill install flags, fixture-friendly destination overrides, conservative replace behavior, and docs/tests that guard Codex skill discovery boundaries. The Python core operation layer remains unchanged.

**Tech Stack:** PowerShell, POSIX `sh`, Python standard library tests with `pytest`, existing Codex adapter files under `integrations/codex/`.

## Global Constraints

- R4.1 must not add runtime dependencies; `pyproject.toml` must keep `dependencies = []`.
- R4.1 must not change neutral core operation behavior.
- R4.1 must not implement marketplace-grade Codex plugin publication.
- R4.1 must not implement Claude adapter reconstruction.
- R4.1 must not edit global Codex configuration automatically.
- User-level skill installation must require an explicit install flag.
- Repo-local install behavior must remain available.
- Windows support must be native PowerShell and must not require WSL or Git Bash.
- Docs and tests must avoid private local absolute paths.
- Commit messages must be written in Chinese.

---

## File Structure

- Modify `integrations/codex/install/install.ps1`: add explicit user-level skill install flags, dry-run output, destination override, replace guard, and optional repo-local argument validation.
- Modify `integrations/codex/install/install.sh`: add POSIX equivalent flags and behavior.
- Modify `tests/unit/test_codex_installer_smoke.py`: add runtime and static tests for user-level skill install behavior.
- Create `tests/unit/test_r4_1_user_skill_install_docs.py`: guard docs, roadmap, Codex manual alignment, and deferred boundaries.
- Modify `integrations/codex/install/README.md`: document repo-local and user-level skill install examples.
- Modify `integrations/codex/README.md`: document R4.1 user-level skill mode as explicit and dry-run capable.
- Modify `integrations/codex/skills/README.md`: document `$HOME/.agents/skills/llm-wiki` and verification prompts.
- Modify `docs/adapter-packaging-plan.md`: update R4.1 install strategy.
- Modify `docs/roadmap-schedule.md`: add R4.1 planning entry.
- Do not modify neutral core Python operation files.

---

### Task 1: PowerShell User-Level Skill Install

**Files:**
- Modify: `integrations/codex/install/install.ps1`
- Modify: `tests/unit/test_codex_installer_smoke.py`

**Interfaces:**
- Consumes: existing `integrations/codex/skills/llm-wiki/SKILL.md`
- Produces: PowerShell flags `-InstallUserSkill`, `-SkillDestination <path>`, and `-ReplaceUserSkill`

- [ ] **Step 1: Add failing PowerShell dry-run and copy tests**

Append these tests to `tests/unit/test_codex_installer_smoke.py`:

```python
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
```

- [ ] **Step 2: Run the new PowerShell tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_dry_run_does_not_write_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_copies_skill_to_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_refuses_different_existing_destination -q
```

Expected: fail because `install.ps1` does not yet accept user-level skill install flags.

- [ ] **Step 3: Implement PowerShell user skill install**

Update `integrations/codex/install/install.ps1` with these required behaviors:

```powershell
param(
  [string]$VaultPath,
  [string]$Purpose,
  [switch]$DryRun,
  [switch]$InstallUserSkill,
  [string]$SkillDestination,
  [switch]$ReplaceUserSkill
)
```

Add helper behavior:

- `$SkillSource = Join-Path $RepoRoot "integrations\codex\skills\llm-wiki"`
- default `$SkillDestination` to `Join-Path $HOME ".agents\skills\llm-wiki"` when empty;
- validate source `SKILL.md` contains `name: llm-wiki` and `description:`;
- if `-InstallUserSkill -DryRun`, print `DRY RUN: Install Codex user skill from "<source>" to "<destination>"`;
- if destination exists and differs, throw `Codex user skill destination already exists and differs. Re-run with -ReplaceUserSkill to replace it.`;
- if destination exists and is identical, print `Codex user skill already installed at "<destination>"`;
- if replacing, remove only the destination skill directory, never a parent directory;
- copy source directory recursively to destination;
- print `Codex user skill installed at "<destination>"`;
- print verification prompts:
  - `Next Codex prompt: check wiki status`
  - `Next Codex prompt: search wiki for durable knowledge`

Keep repo-local install compatible:

- if `-InstallUserSkill` is absent, require both `-VaultPath` and `-Purpose`;
- existing repo-local dry-run output must still include `pip install -e`, `llm-wiki init`, `llm-wiki detect-transport`, `llm-wiki status`, and `llm-wiki continue`.

- [ ] **Step 4: Run PowerShell installer tests**

Run:

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py -q
```

Expected on Windows: PowerShell tests pass and POSIX runtime test keeps its existing skip.

- [ ] **Step 5: Commit Task 1**

Run:

```powershell
git add integrations/codex/install/install.ps1 tests/unit/test_codex_installer_smoke.py
git commit -m "实现 R4.1 PowerShell 用户级技能安装"
```

---

### Task 2: POSIX Shell User-Level Skill Install

**Files:**
- Modify: `integrations/codex/install/install.sh`
- Modify: `tests/unit/test_codex_installer_smoke.py`

**Interfaces:**
- Consumes: PowerShell behavior names from Task 1 for parity.
- Produces: shell flags `--install-user-skill`, `--skill-destination PATH`, and `--replace-user-skill`

- [ ] **Step 1: Add failing shell static and runtime tests**

Append these tests to `tests/unit/test_codex_installer_smoke.py`:

```python
def test_shell_installer_documents_user_skill_install_flags() -> None:
    text = (_repo_root() / "integrations" / "codex" / "install" / "install.sh").read_text(encoding="utf-8")

    assert "--install-user-skill" in text
    assert "--skill-destination" in text
    assert "--replace-user-skill" in text
    assert "$HOME/.agents/skills/llm-wiki" in text


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
```

- [ ] **Step 2: Run shell tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py::test_shell_installer_documents_user_skill_install_flags tests/unit/test_codex_installer_smoke.py::test_shell_user_skill_install_dry_run_does_not_write_destination tests/unit/test_codex_installer_smoke.py::test_shell_user_skill_install_copies_skill_to_destination -q
```

Expected on Windows: static test fails; runtime tests skip. On POSIX: tests fail until script supports flags.

- [ ] **Step 3: Implement shell user skill install parity**

Update `integrations/codex/install/install.sh`:

- parse `--dry-run`, `--install-user-skill`, `--skill-destination PATH`, and `--replace-user-skill`;
- set default destination to `$HOME/.agents/skills/llm-wiki`;
- validate source `SKILL.md` contains `name: llm-wiki` and `description:`;
- if `--install-user-skill --dry-run`, print `DRY RUN: Install Codex user skill from "<source>" to "<destination>"`;
- if destination exists and differs, exit non-zero with `Codex user skill destination already exists and differs. Re-run with --replace-user-skill to replace it.`;
- if destination exists and is identical, print `Codex user skill already installed at "<destination>"`;
- copy source to destination with portable `mkdir -p` and `cp -R`;
- preserve existing repo-local install behavior when `--install-user-skill` is absent.

- [ ] **Step 4: Run installer smoke tests**

Run:

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py -q
```

Expected on Windows: all non-POSIX checks pass and POSIX runtime checks skip.

- [ ] **Step 5: Commit Task 2**

Run:

```powershell
git add integrations/codex/install/install.sh tests/unit/test_codex_installer_smoke.py
git commit -m "实现 R4.1 Shell 用户级技能安装"
```

---

### Task 3: R4.1 Documentation And Guard Tests

**Files:**
- Create: `tests/unit/test_r4_1_user_skill_install_docs.py`
- Modify: `integrations/codex/install/README.md`
- Modify: `integrations/codex/README.md`
- Modify: `integrations/codex/skills/README.md`
- Modify: `docs/adapter-packaging-plan.md`
- Modify: `docs/roadmap-schedule.md`

**Interfaces:**
- Consumes: installer flags from Tasks 1 and 2.
- Produces: public docs that describe explicit user-level skill installation and deferred boundaries.

- [ ] **Step 1: Add failing R4.1 docs tests**

Create `tests/unit/test_r4_1_user_skill_install_docs.py`:

```python
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


def test_r4_1_docs_have_no_private_paths_or_damaged_text() -> None:
    damaged = ["\ufffd", "闁", "娑", "閻", "闂", "濡ょ姴鐭侀惁"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\"]

    for relative in DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"


def test_install_readme_documents_explicit_user_skill_install() -> None:
    text = _read("integrations/codex/install/README.md")

    assert ".\\install.ps1 -InstallUserSkill -DryRun" in text
    assert ".\\install.ps1 -InstallUserSkill" in text
    assert "./install.sh --install-user-skill --dry-run" in text
    assert "./install.sh --install-user-skill" in text
    assert "$HOME/.agents/skills/llm-wiki" in text
    assert "does not edit global Codex configuration automatically" in text
    assert "Use `-SkillDestination <path>` or `--skill-destination <path>` for tests or advanced installs." in text


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
    assert "Status: planned." in schedule
    assert "Explicit `-InstallUserSkill` and `--install-user-skill` paths." in schedule
```

- [ ] **Step 2: Run docs tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r4_1_user_skill_install_docs.py -q
```

Expected: fail because docs do not yet document R4.1.

- [ ] **Step 3: Update docs**

Update the listed docs to include:

- user-level destination `$HOME/.agents/skills/llm-wiki`;
- PowerShell examples:
  - `.\install.ps1 -InstallUserSkill -DryRun`
  - `.\install.ps1 -InstallUserSkill`
- shell examples:
  - `./install.sh --install-user-skill --dry-run`
  - `./install.sh --install-user-skill`
- destination override:
  - `-SkillDestination <path>`
  - `--skill-destination <path>`
- no automatic global Codex configuration edits;
- restart or start a new Codex session after installing;
- plugin publication and Claude adapter reconstruction remain deferred.

- [ ] **Step 4: Run docs and related installer tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_1_user_skill_install_docs.py tests/unit/test_codex_installer_smoke.py -q
```

Expected on Windows: tests pass with existing POSIX runtime skips.

- [ ] **Step 5: Commit Task 3**

Run:

```powershell
git add tests/unit/test_r4_1_user_skill_install_docs.py integrations/codex/install/README.md integrations/codex/README.md integrations/codex/skills/README.md docs/adapter-packaging-plan.md docs/roadmap-schedule.md
git commit -m "补充 R4.1 用户级技能安装文档"
```

---

### Task 4: Final R4.1 Verification And Progress Record

**Files:**
- Modify: external `codex_doc/project_understanding_progress.md`
- No repository code changes unless verification exposes a defect.

**Interfaces:**
- Consumes: R4.1 task commits.
- Produces: verified branch state and an external progress record.

- [ ] **Step 1: Run focused R4.1 tests**

Run:

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py tests/unit/test_r4_1_user_skill_install_docs.py -q
```

Expected on Windows: PowerShell tests and docs tests pass; POSIX runtime tests skip.

- [ ] **Step 2: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with expected platform skips allowed.

- [ ] **Step 3: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no whitespace errors.

- [ ] **Step 4: Confirm dependency boundary**

Run:

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies = \[\]"
```

Expected output includes:

```text
dependencies = []
```

- [ ] **Step 5: Confirm branch status and tracked scratch files**

Run:

```powershell
git status --short --branch
git ls-files .superpowers codex_doc
git log --oneline -8
```

Expected:

- branch is `r4-1-codex-user-skill-installation-design`;
- working tree is clean before final review;
- `.superpowers` and in-repository `codex_doc` are not tracked;
- recent R4.1 commits use Chinese commit messages.

- [ ] **Step 6: Update external progress document**

Append a stage to external `codex_doc/project_understanding_progress.md` recording:

- R4.1 implementation commits;
- focused test result;
- full test result;
- whitespace check result;
- dependency boundary result;
- remaining deferred boundaries.

- [ ] **Step 7: Report final R4.1 status**

Report:

- branch name;
- latest commit hash;
- focused test result;
- full test result;
- whitespace check result;
- dependency boundary result;
- reminder that plugin marketplace publication and Claude adapter reconstruction remain deferred.
