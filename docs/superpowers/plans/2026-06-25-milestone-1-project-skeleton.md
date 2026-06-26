# Milestone 1 Project Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 `llm-wiki-core` 的最小 Python 项目骨架、测试骨架和 adapter 占位文档，但不实现 ingest/query/lint/save 等业务逻辑。

**Architecture:** 第一阶段只建立可测试的空骨架：core package 独立于 adapter，Codex/Claude 集成放在 `integrations/`，测试夹具放在 `tests/fixtures/`。业务语义仍以现有 planning docs 为准，后续 Milestone 才逐步实现 operation。

**Tech Stack:** Python 3.10+，标准库优先，pytest 用于测试，PowerShell 为 Windows 原生命令示例。

## Global Constraints

- Karpathy gist 是 canonical source。
- `claude-obsidian` 是 reference implementation，不复制其 Claude 专属实现。
- `llm-wiki-core` 是中性 practice variant。
- 当前实现只支持本地 Codex App + Codex CLI 目标路径。
- Windows 原生优先，不依赖 WSL / Git Bash。
- Core logic 使用 Python；PowerShell / shell 只做薄入口。
- Filesystem transport 必须可用；Obsidian CLI 是 optional preferred transport。
- MVP 采用 artifact-level equivalence，不追求 LLM-authored content 字节级一致。
- 第一阶段不实现完整 ingest/query/lint/save 业务逻辑。
- `D:/ai/llmWiki` 不是 Git 仓库；不得修改 `D:/ai/llmWiki/claude-obsidian`。
- 若后续需要 Git commit，commit message 使用中文。

---

## File Structure

第一阶段创建或修改以下文件：

- Create: `D:/ai/llmWiki/llm-wiki-core/pyproject.toml`  
  负责声明 Python package metadata、Python 版本和 pytest 配置。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/__init__.py`  
  暴露包版本。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/cli.py`  
  提供最小 CLI 入口，只支持 `--version` 和 help。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/*.py`  
  创建 operation 模块占位，不实现业务逻辑。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/schema/*.py`  
  创建 schema 模块占位，不实现完整解析。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/*.py`  
  创建 transport 模块占位，不实现检测逻辑。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/*.py`  
  创建 vault 模块占位，不创建 vault 文件。
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/validation/*.py`  
  创建 validation 模块占位。
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_package_skeleton.py`  
  验证 package 和模块可 import。
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/*/README.md`  
  创建测试夹具目录说明。
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/*`  
  创建 Codex adapter 占位文档。
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/claude/README.md`  
  保留 Claude adapter 边界说明。
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`  
  补充项目骨架状态和测试命令。
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`  
  完成阶段后追加进展总结。

---

### Task 1: Python Project Metadata

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/pyproject.toml`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/cli.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_package_skeleton.py`

**Interfaces:**
- Consumes: existing planning docs in `D:/ai/llmWiki/llm-wiki-core/docs/`
- Produces: package version `llm_wiki_core.__version__`, CLI entry function `llm_wiki_core.cli.main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Create the package and test directories**

Run:

```powershell
New-Item -ItemType Directory -Path `
  'D:\ai\llmWiki\llm-wiki-core\llm_wiki_core', `
  'D:\ai\llmWiki\llm-wiki-core\tests\unit' -Force | Out-Null
```

Expected: command exits with code 0.

- [ ] **Step 2: Create `pyproject.toml`**

Create `D:/ai/llmWiki/llm-wiki-core/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "llm-wiki-core"
version = "0.1.0"
description = "Neutral LLM Wiki core inspired by Karpathy's llm-wiki pattern."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [
  { name = "llm-wiki-core contributors" }
]
dependencies = []

[project.scripts]
llm-wiki = "llm_wiki_core.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-ra"
```

- [ ] **Step 3: Create package version file**

Create `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/__init__.py`:

```python
"""Neutral core for local LLM-maintained Markdown wiki workflows."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Create minimal CLI entry**

Create `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/cli.py`:

```python
from __future__ import annotations

import argparse

from llm_wiki_core import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-wiki",
        description="Neutral LLM Wiki core command line entry.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"llm-wiki-core {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0
```

- [ ] **Step 5: Write package skeleton tests**

Create `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_package_skeleton.py`:

```python
from __future__ import annotations

import pytest

import llm_wiki_core
from llm_wiki_core.cli import main


def test_package_exposes_version() -> None:
    assert llm_wiki_core.__version__ == "0.1.0"


def test_cli_help_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "Neutral LLM Wiki core" in capsys.readouterr().out


def test_cli_without_arguments_exits_successfully() -> None:
    assert main([]) == 0
```

- [ ] **Step 6: Run tests**

Run:

```powershell
Set-Location 'D:\ai\llmWiki\llm-wiki-core'
python -m pytest tests\unit\test_package_skeleton.py -q
```

Expected: `3 passed`.

---

### Task 2: Core Module Skeleton

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/init.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/status.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/continue_.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/ingest.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/query.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/lint.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/save.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/detect_transport.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/schema/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/schema/manifest.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/schema/frontmatter.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/schema/wikilinks.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/filesystem.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/obsidian_cli.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/snapshot.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/paths.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/scaffold.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/index.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/log.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/vault/hot.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/validation/__init__.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/validation/lint_report.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/validation/parity.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_package_skeleton.py`

**Interfaces:**
- Consumes: module layout from `docs/project-skeleton-plan.md`
- Produces: importable module names matching future operation contracts

- [ ] **Step 1: Create core module directories**

Run:

```powershell
New-Item -ItemType Directory -Path `
  'D:\ai\llmWiki\llm-wiki-core\llm_wiki_core\operations', `
  'D:\ai\llmWiki\llm-wiki-core\llm_wiki_core\schema', `
  'D:\ai\llmWiki\llm-wiki-core\llm_wiki_core\transport', `
  'D:\ai\llmWiki\llm-wiki-core\llm_wiki_core\vault', `
  'D:\ai\llmWiki\llm-wiki-core\llm_wiki_core\validation' -Force | Out-Null
```

Expected: command exits with code 0.

- [ ] **Step 2: Create package marker files**

Create each `__init__.py` listed above with:

```python
"""Package marker for llm-wiki-core skeleton."""
```

- [ ] **Step 3: Create operation placeholder modules**

Create each operation module listed above with the matching module docstring:

```python
"""Placeholder module for a future llm-wiki-core operation."""
```

Do not add operation functions in Milestone 1.

- [ ] **Step 4: Create schema placeholder modules**

Create each schema module listed above with:

```python
"""Placeholder module for future schema validation helpers."""
```

- [ ] **Step 5: Create transport placeholder modules**

Create each transport module listed above with:

```python
"""Placeholder module for future transport helpers."""
```

- [ ] **Step 6: Create vault placeholder modules**

Create each vault module listed above with:

```python
"""Placeholder module for future vault file helpers."""
```

- [ ] **Step 7: Create validation placeholder modules**

Create each validation module listed above with:

```python
"""Placeholder module for future validation helpers."""
```

- [ ] **Step 8: Extend import tests**

Append to `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_package_skeleton.py`:

```python
def test_core_skeleton_modules_import() -> None:
    import llm_wiki_core.operations.continue_
    import llm_wiki_core.operations.detect_transport
    import llm_wiki_core.operations.ingest
    import llm_wiki_core.operations.init
    import llm_wiki_core.operations.lint
    import llm_wiki_core.operations.query
    import llm_wiki_core.operations.save
    import llm_wiki_core.operations.status
    import llm_wiki_core.schema.frontmatter
    import llm_wiki_core.schema.manifest
    import llm_wiki_core.schema.wikilinks
    import llm_wiki_core.transport.filesystem
    import llm_wiki_core.transport.obsidian_cli
    import llm_wiki_core.transport.snapshot
    import llm_wiki_core.validation.lint_report
    import llm_wiki_core.validation.parity
    import llm_wiki_core.vault.hot
    import llm_wiki_core.vault.index
    import llm_wiki_core.vault.log
    import llm_wiki_core.vault.paths
    import llm_wiki_core.vault.scaffold
```

- [ ] **Step 9: Run tests**

Run:

```powershell
Set-Location 'D:\ai\llmWiki\llm-wiki-core'
python -m pytest tests\unit\test_package_skeleton.py -q
```

Expected: `4 passed`.

---

### Task 3: Test Fixture Directory Skeleton

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f0-empty/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f1-fresh-vault/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f2-single-source/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f3-existing-knowledge/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f4-broken-wiki/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_fixture_skeleton.py`

**Interfaces:**
- Consumes: `docs/test-fixture-plan.md`
- Produces: fixture directory names used by future parity tests

- [ ] **Step 1: Create fixture directories**

Run:

```powershell
New-Item -ItemType Directory -Path `
  'D:\ai\llmWiki\llm-wiki-core\tests\fixtures\f0-empty', `
  'D:\ai\llmWiki\llm-wiki-core\tests\fixtures\f1-fresh-vault', `
  'D:\ai\llmWiki\llm-wiki-core\tests\fixtures\f2-single-source', `
  'D:\ai\llmWiki\llm-wiki-core\tests\fixtures\f3-existing-knowledge', `
  'D:\ai\llmWiki\llm-wiki-core\tests\fixtures\f4-broken-wiki' -Force | Out-Null
```

Expected: command exits with code 0.

- [ ] **Step 2: Create fixture root README**

Create `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/README.md`:

```markdown
# Test Fixtures

These fixtures support artifact-level parity tests for the LLM Wiki MVP.

Fixture definitions are governed by `docs/test-fixture-plan.md`.
```

- [ ] **Step 3: Create per-fixture README files**

Create `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f0-empty/README.md`:

```markdown
# F0 Empty Directory

Purpose: validate `init`.
```

Create `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f1-fresh-vault/README.md`:

```markdown
# F1 Fresh Vault

Purpose: validate `status`, `continue`, and basic `lint`.
```

Create `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f2-single-source/README.md`:

```markdown
# F2 Single Raw Source

Purpose: validate single-source `ingest`.
```

Create `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f3-existing-knowledge/README.md`:

```markdown
# F3 Existing Knowledge

Purpose: validate `query` and `save`.
```

Create `D:/ai/llmWiki/llm-wiki-core/tests/fixtures/f4-broken-wiki/README.md`:

```markdown
# F4 Broken Wiki

Purpose: validate `lint` findings.
```

- [ ] **Step 4: Create fixture skeleton tests**

Create `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_fixture_skeleton.py`:

```python
from __future__ import annotations

from pathlib import Path


def test_fixture_directories_exist() -> None:
    root = Path(__file__).parents[1] / "fixtures"

    expected = {
        "f0-empty",
        "f1-fresh-vault",
        "f2-single-source",
        "f3-existing-knowledge",
        "f4-broken-wiki",
    }

    actual = {path.name for path in root.iterdir() if path.is_dir()}
    assert expected.issubset(actual)


def test_each_fixture_has_readme() -> None:
    root = Path(__file__).parents[1] / "fixtures"

    for fixture in [
        "f0-empty",
        "f1-fresh-vault",
        "f2-single-source",
        "f3-existing-knowledge",
        "f4-broken-wiki",
    ]:
        assert (root / fixture / "README.md").is_file()
```

- [ ] **Step 5: Run tests**

Run:

```powershell
Set-Location 'D:\ai\llmWiki\llm-wiki-core'
python -m pytest tests\unit\test_fixture_skeleton.py -q
```

Expected: `2 passed`.

---

### Task 4: Adapter Placeholder Skeleton

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/AGENTS.template.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/skills/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/plugin/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/install/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/integrations/claude/README.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_integration_skeleton.py`

**Interfaces:**
- Consumes: `docs/adapter-packaging-plan.md`, `docs/codex-command-contract.md`
- Produces: adapter directories without runtime-specific code

- [ ] **Step 1: Create adapter directories**

Run:

```powershell
New-Item -ItemType Directory -Path `
  'D:\ai\llmWiki\llm-wiki-core\integrations\codex\skills', `
  'D:\ai\llmWiki\llm-wiki-core\integrations\codex\plugin', `
  'D:\ai\llmWiki\llm-wiki-core\integrations\codex\install', `
  'D:\ai\llmWiki\llm-wiki-core\integrations\claude' -Force | Out-Null
```

Expected: command exits with code 0.

- [ ] **Step 2: Create Codex integration README**

Create `D:/ai/llmWiki/llm-wiki-core/integrations/codex/README.md`:

```markdown
# Codex Adapter

This directory is reserved for Codex App and Codex CLI integration assets.

The adapter must call into the neutral core contracts instead of redefining LLM Wiki behavior.
```

- [ ] **Step 3: Create Codex AGENTS template**

Create `D:/ai/llmWiki/llm-wiki-core/integrations/codex/AGENTS.template.md`:

```markdown
# LLM Wiki Agent Instructions

Use this vault according to the LLM Wiki pattern:

- Treat `.raw/` as immutable source material.
- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.
- Follow the operation contracts in `docs/operation-contract.md`.
```

- [ ] **Step 4: Create Codex placeholder docs**

Create `D:/ai/llmWiki/llm-wiki-core/integrations/codex/skills/README.md`:

```markdown
# Codex Skills

Future Codex skill packaging will live here after the core MVP contracts are implemented.
```

Create `D:/ai/llmWiki/llm-wiki-core/integrations/codex/plugin/README.md`:

```markdown
# Codex Plugin

Future Codex plugin metadata will live here. Plugin packaging is not required for Milestone 1.
```

Create `D:/ai/llmWiki/llm-wiki-core/integrations/codex/install/README.md`:

```markdown
# Installers

Future PowerShell and macOS shell entrypoints will live here. Milestone 1 does not create installer scripts.
```

- [ ] **Step 5: Create Claude boundary README**

Create `D:/ai/llmWiki/llm-wiki-core/integrations/claude/README.md`:

```markdown
# Claude Adapter

This directory is reserved for future Claude Code adapter work.

Claude-specific plugin manifests, hooks, slash commands, and subagent behavior must stay out of the neutral core.
```

- [ ] **Step 6: Create integration skeleton tests**

Create `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_integration_skeleton.py`:

```python
from __future__ import annotations

from pathlib import Path


def test_codex_adapter_placeholders_exist() -> None:
    root = Path(__file__).parents[2]
    codex = root / "integrations" / "codex"

    assert (codex / "README.md").is_file()
    assert (codex / "AGENTS.template.md").is_file()
    assert (codex / "skills" / "README.md").is_file()
    assert (codex / "plugin" / "README.md").is_file()
    assert (codex / "install" / "README.md").is_file()


def test_claude_adapter_boundary_exists() -> None:
    root = Path(__file__).parents[2]
    readme = root / "integrations" / "claude" / "README.md"

    assert readme.is_file()
    assert "must stay out of the neutral core" in readme.read_text(encoding="utf-8")
```

- [ ] **Step 7: Run tests**

Run:

```powershell
Set-Location 'D:\ai\llmWiki\llm-wiki-core'
python -m pytest tests\unit\test_integration_skeleton.py -q
```

Expected: `2 passed`.

---

### Task 5: README Update And Full Verification

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: test results from Tasks 1-4
- Produces: documented Milestone 1 skeleton state

- [ ] **Step 1: Update README with skeleton status**

Append this section to `D:/ai/llmWiki/llm-wiki-core/README.md`:

```markdown
## Development Status

Milestone 1 creates only the project skeleton:

- Python package metadata.
- Importable core module placeholders.
- Test fixture directories.
- Codex and Claude adapter placeholder directories.

It does not implement ingest, query, lint, save, transport detection, or installer behavior.

Run skeleton tests:

```powershell
python -m pytest
```
```

- [ ] **Step 2: Run the full test suite**

Run:

```powershell
Set-Location 'D:\ai\llmWiki\llm-wiki-core'
python -m pytest -q
```

Expected: `8 passed`.

- [ ] **Step 3: Confirm no `claude-obsidian` files changed**

Run:

```powershell
Set-Location 'D:\ai\llmWiki\claude-obsidian'
git status --short
```

Expected: no changes caused by Milestone 1. If pre-existing user changes are present, report them without reverting.

- [ ] **Step 4: Update progress document**

Append to `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`:

```markdown
## 阶段 30：Milestone 1 项目骨架创建

状态：已完成

### 本阶段实际产物

- 创建 `llm-wiki-core` Python package skeleton。
- 创建 tests fixture skeleton。
- 创建 Codex adapter placeholder。
- 创建 Claude adapter boundary placeholder。
- 更新 README development status。

### 验证

- `python -m pytest -q` 通过。
- 未修改 `claude-obsidian`。

### 本阶段边界

- 未实现 ingest/query/lint/save 业务逻辑。
- 未实现 Obsidian CLI transport。
- 未创建 installer 脚本。
- 未进行 Git commit 或远端操作。
```

- [ ] **Step 5: Git note**

Do not run `git commit` in Milestone 1 unless the user first confirms repository strategy for `llm-wiki-core`. Current known state: `D:/ai/llmWiki` is not a Git repository, and `D:/ai/llmWiki/claude-obsidian` is a separate upstream Git repository that must not be polluted.

---

## Self-Review

### Spec Coverage

- Karpathy pattern remains the canonical source: covered by Global Constraints.
- `claude-obsidian` remains reference implementation only: covered by Global Constraints and Task 4.
- Windows native path: all commands use PowerShell.
- No WSL/Git Bash dependency: covered by Global Constraints.
- No business logic in Milestone 1: covered by each task boundary.
- Codex App / CLI target path: covered by Codex adapter placeholder.
- `claude-obsidian` untouched: covered by Task 5 Step 3.

### Placeholder Scan

This plan intentionally creates placeholder modules and placeholder adapter docs only because Milestone 1 is a skeleton milestone. No operation behavior is left unspecified inside an implemented function because no operation functions are created.

### Type Consistency

- `llm_wiki_core.__version__` is defined in Task 1 and used by `llm_wiki_core.cli`.
- `main(argv: list[str] | None = None) -> int` is defined in Task 1 and tested in Task 1.
- Future operation module names match `docs/project-skeleton-plan.md`.

## Execution Handoff

Plan complete and saved to `D:/ai/llmWiki/llm-wiki-core/docs/superpowers/plans/2026-06-25-milestone-1-project-skeleton.md`.

Two execution options after the user explicitly confirms `开始创建项目骨架和 MVP 实现代码`:

1. **Subagent-Driven** - dispatch a fresh worker per task, review between tasks.
2. **Inline Execution** - execute tasks in this session with checkpoints.
