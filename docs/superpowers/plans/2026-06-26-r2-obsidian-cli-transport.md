# R2 Obsidian CLI Transport Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an official Obsidian CLI transport that can become runtime-eligible only after vault binding and read/write/append/list/search capability probes pass, while preserving filesystem fallback.

**Architecture:** Add a small official `obsidian` CLI command profile and runner boundary, then replace the contract-only `ObsidianCliTransport` with a tested implementation that still uses the neutral transport interface. Extend detection snapshots with official-vs-legacy CLI metadata and capability fields. Make runtime selection capability-aware so operations continue to use filesystem unless official Obsidian CLI is verified for the target vault.

**Tech Stack:** Python 3.10+, dataclasses, pathlib, subprocess without shell invocation, argparse, pytest, Markdown docs.

## Global Constraints

- Karpathy LLM Wiki gist remains the abstract design source.
- `claude-obsidian` remains the reference implementation, not code to copy.
- `llm-wiki-core` remains neutral across Codex, Claude Code, and future local agents.
- R2 uses official `obsidian` as the only runtime candidate.
- Legacy `obsidian-cli` remains detected but unimplemented.
- Filesystem remains the safe fallback in all unverified cases.
- Automated tests must not require Obsidian to be installed, running, or configured.
- `init` remains filesystem-based.
- R2 must not move the `v0.1.0-mvp` tag.
- R2 must not modify `D:/ai/llmWiki/claude-obsidian`.
- Git commit messages must be Chinese.

---

## File Structure

- `llm_wiki_core/transport/obsidian_cli_runner.py`
  - New official CLI runner boundary, command profile, and subprocess result dataclasses.
- `llm_wiki_core/transport/obsidian_cli.py`
  - Replace the contract-only transport with real read/write/append/exists/list/search behavior using the runner boundary.
- `llm_wiki_core/operations/detect_transport.py`
  - Extend snapshot metadata and add official CLI capability probing.
- `llm_wiki_core/transport/runtime.py`
  - Select `ObsidianCliTransport` only when snapshot metadata proves it is available, implemented, and capability-complete.
- `llm_wiki_core/transport/__init__.py`
  - Export new runner/profile/error types needed by tests and future adapters.
- `llm_wiki_core/cli.py`
  - Print warnings for human-readable `status`, `continue`, and `detect-transport` output when warning lists are present.
- `tests/unit/test_obsidian_cli_command_profile.py`
  - New command builder and subprocess runner tests.
- `tests/unit/test_obsidian_cli_transport.py`
  - Replace contract-only expectations with real fake-runner transport tests.
- `tests/unit/test_transport_detection.py`
  - Extend detection tests for official `obsidian`, legacy `obsidian-cli`, probe success, and probe failure.
- `tests/unit/test_runtime_transport_selection.py`
  - Extend runtime selector tests for official Obsidian CLI eligibility and fallback.
- `tests/unit/test_status_continue_operations.py`
  - Add CLI warning-output tests.
- `tests/unit/test_r2_obsidian_cli_docs.py`
  - New documentation guard test.
- `docs/transport-contract.md`
  - Document official CLI runtime eligibility and legacy CLI boundary.
- `docs/roadmap-schedule.md`
  - Mark R2 implementation outcome when complete.
- `docs/user-guide.md`
  - Add Obsidian CLI setup and troubleshooting notes.
- `docs/r2-obsidian-cli-transport-report.md`
  - New R2 report and verification record.
- `README.md`
  - Add a concise note only if user-facing behavior changes need front-page visibility.
- `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`
  - Update after each completed stage.

---

### Task 1: Official Obsidian CLI Command Profile And Runner

**Files:**
- Create: `llm_wiki_core/transport/obsidian_cli_runner.py`
- Create: `tests/unit/test_obsidian_cli_command_profile.py`
- Modify: `llm_wiki_core/transport/__init__.py`

**Interfaces:**
- Produces: `ObsidianCliRunResult(argv: list[str], returncode: int, stdout: str, stderr: str)`.
- Produces: `ObsidianCliRunner.run(argv: list[str], timeout_seconds: int) -> ObsidianCliRunResult`.
- Produces: `SubprocessObsidianCliRunner.run(...)`.
- Produces: `ObsidianCliProfile(executable: str, vault_selector: str, timeout_seconds: int = 10)`.
- Produces command builders:
  - `help_argv() -> list[str]`
  - `read_argv(relative_path: str) -> list[str]`
  - `write_argv(relative_path: str, content: str) -> list[str]`
  - `append_argv(relative_path: str, content: str) -> list[str]`
  - `files_argv(root: str = "wiki") -> list[str]`
  - `search_argv(query: str, root: str = "wiki") -> list[str]`

- [ ] **Step 1: Write failing command profile tests**

Create `tests/unit/test_obsidian_cli_command_profile.py` with:

```python
from __future__ import annotations


def test_official_obsidian_profile_builds_name_value_commands() -> None:
    from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliProfile

    profile = ObsidianCliProfile(executable="obsidian", vault_selector="Research Vault")

    assert profile.help_argv() == ["obsidian", "--help"]
    assert profile.read_argv("wiki/index.md") == [
        "obsidian",
        "read",
        "vault=Research Vault",
        "path=wiki/index.md",
    ]
    assert profile.write_argv("wiki/notes/热缓存.md", "line 1\nline 2\n") == [
        "obsidian",
        "create",
        "vault=Research Vault",
        "path=wiki/notes/热缓存.md",
        "content=line 1\nline 2\n",
        "overwrite=true",
    ]
    assert profile.append_argv("wiki/log.md", "append\n") == [
        "obsidian",
        "append",
        "vault=Research Vault",
        "path=wiki/log.md",
        "content=append\n",
    ]
    assert profile.files_argv("wiki") == [
        "obsidian",
        "files",
        "vault=Research Vault",
        "path=wiki",
    ]
    assert profile.search_argv("hot cache", "wiki") == [
        "obsidian",
        "search:context",
        "vault=Research Vault",
        "query=hot cache",
        "path=wiki",
    ]


def test_subprocess_runner_captures_stdout_stderr_and_return_code() -> None:
    from llm_wiki_core.transport.obsidian_cli_runner import SubprocessObsidianCliRunner

    runner = SubprocessObsidianCliRunner()
    result = runner.run(
        [
            "python",
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)",
        ],
        timeout_seconds=5,
    )

    assert result.returncode == 3
    assert result.stdout.strip() == "out"
    assert result.stderr.strip() == "err"
    assert result.argv[0] == "python"
```

- [ ] **Step 2: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_obsidian_cli_command_profile.py -q
```

Expected: fails with `ModuleNotFoundError` for `llm_wiki_core.transport.obsidian_cli_runner`.

- [ ] **Step 3: Implement runner and profile**

Create `llm_wiki_core/transport/obsidian_cli_runner.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import subprocess


@dataclass(frozen=True)
class ObsidianCliRunResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str


class ObsidianCliRunner(Protocol):
    def run(self, argv: list[str], timeout_seconds: int) -> ObsidianCliRunResult:
        ...


class SubprocessObsidianCliRunner:
    def run(self, argv: list[str], timeout_seconds: int) -> ObsidianCliRunResult:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout_seconds,
            check=False,
        )
        return ObsidianCliRunResult(
            argv=list(argv),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


@dataclass(frozen=True)
class ObsidianCliProfile:
    executable: str
    vault_selector: str
    timeout_seconds: int = 10

    def help_argv(self) -> list[str]:
        return [self.executable, "--help"]

    def read_argv(self, relative_path: str) -> list[str]:
        return [self.executable, "read", self._vault_arg(), f"path={relative_path}"]

    def write_argv(self, relative_path: str, content: str) -> list[str]:
        return [
            self.executable,
            "create",
            self._vault_arg(),
            f"path={relative_path}",
            f"content={content}",
            "overwrite=true",
        ]

    def append_argv(self, relative_path: str, content: str) -> list[str]:
        return [
            self.executable,
            "append",
            self._vault_arg(),
            f"path={relative_path}",
            f"content={content}",
        ]

    def files_argv(self, root: str = "wiki") -> list[str]:
        return [self.executable, "files", self._vault_arg(), f"path={root}"]

    def search_argv(self, query: str, root: str = "wiki") -> list[str]:
        return [self.executable, "search:context", self._vault_arg(), f"query={query}", f"path={root}"]

    def _vault_arg(self) -> str:
        return f"vault={self.vault_selector}"
```

Update `llm_wiki_core/transport/__init__.py`:

```python
from llm_wiki_core.transport.obsidian_cli_runner import (
    ObsidianCliProfile,
    ObsidianCliRunner,
    ObsidianCliRunResult,
    SubprocessObsidianCliRunner,
)
```

Add the four names to `__all__`.

- [ ] **Step 4: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_obsidian_cli_command_profile.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

Run:

```powershell
git add llm_wiki_core/transport/obsidian_cli_runner.py llm_wiki_core/transport/__init__.py tests/unit/test_obsidian_cli_command_profile.py
git commit -m "新增官方 Obsidian CLI 命令构造"
```

---

### Task 2: Obsidian CLI Transport Implementation

**Files:**
- Modify: `llm_wiki_core/transport/obsidian_cli.py`
- Modify: `tests/unit/test_obsidian_cli_transport.py`

**Interfaces:**
- Consumes: `ObsidianCliProfile`, `ObsidianCliRunner`, `ObsidianCliRunResult`.
- Produces: `ObsidianCliTransport(vault_root, executable, vault_selector, runner=None, timeout_seconds=10)`.
- Produces errors:
  - `ObsidianCliTransportError`
  - `ObsidianCliCommandError`
  - `ObsidianCliTimeoutError`
  - `ObsidianCliParseError`
- Produces methods compatible with `FilesystemTransport`:
  - `read_text(relative_path) -> str`
  - `write_text(relative_path, content) -> str`
  - `append_text(relative_path, content) -> str`
  - `exists(relative_path) -> bool`
  - `list_markdown(root="wiki") -> list[str]`
  - `search_text(query, root="wiki") -> list[SearchResult]`

- [ ] **Step 1: Replace contract-only expectations with failing fake-runner tests**

Replace `tests/unit/test_obsidian_cli_transport.py` with:

```python
from __future__ import annotations

import pytest


class FakeRunner:
    def __init__(self, responses: dict[tuple[str, ...], tuple[int, str, str]]) -> None:
        self.responses = responses
        self.calls: list[list[str]] = []

    def run(self, argv: list[str], timeout_seconds: int):
        from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliRunResult

        self.calls.append(list(argv))
        returncode, stdout, stderr = self.responses.get(tuple(argv), (1, "", "unexpected command"))
        return ObsidianCliRunResult(argv=list(argv), returncode=returncode, stdout=stdout, stderr=stderr)


def test_obsidian_cli_transport_reads_writes_and_appends_text(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "read", "vault=Vault", "path=wiki/index.md"): (0, "# Wiki Index\n", ""),
            (
                "obsidian",
                "create",
                "vault=Vault",
                "path=wiki/concepts/热缓存.md",
                "content=# 热缓存\n",
                "overwrite=true",
            ): (0, "", ""),
            (
                "obsidian",
                "append",
                "vault=Vault",
                "path=wiki/concepts/热缓存.md",
                "content=\ncontext\n",
            ): (0, "", ""),
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    assert transport.read_text("wiki/index.md") == "# Wiki Index\n"
    assert transport.write_text("wiki/concepts/热缓存.md", "# 热缓存\n") == "wiki/concepts/热缓存.md"
    assert transport.append_text("wiki/concepts/热缓存.md", "\ncontext\n") == "wiki/concepts/热缓存.md"


def test_obsidian_cli_transport_lists_markdown_files(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "files", "vault=Vault", "path=wiki"): (
                0,
                "wiki/index.md\nwiki/readme.txt\nwiki/concepts/Hot Cache.md\n",
                "",
            )
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    assert transport.list_markdown("wiki") == ["wiki/concepts/Hot Cache.md", "wiki/index.md"]


def test_obsidian_cli_transport_searches_context_output(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "search:context", "vault=Vault", "query=hot cache", "path=wiki"): (
                0,
                "wiki/concepts/Hot Cache.md:2:Recent context for the agent.\nwiki/index.md:3:- [[Hot Cache]]\n",
                "",
            )
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    results = transport.search_text("hot cache", root="wiki")

    assert [(result.path, result.line_number, result.line) for result in results] == [
        ("wiki/concepts/Hot Cache.md", 2, "Recent context for the agent."),
        ("wiki/index.md", 3, "- [[Hot Cache]]"),
    ]


def test_obsidian_cli_transport_exists_uses_read_result(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "read", "vault=Vault", "path=wiki/index.md"): (0, "# Wiki Index\n", ""),
            ("obsidian", "read", "vault=Vault", "path=wiki/missing.md"): (1, "", "not found"),
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    assert transport.exists("wiki/index.md") is True
    assert transport.exists("wiki/missing.md") is False


def test_obsidian_cli_transport_rejects_unsafe_paths(tmp_path) -> None:
    from llm_wiki_core.transport import PathOutsideVaultError
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=FakeRunner({}))

    with pytest.raises(PathOutsideVaultError):
        transport.read_text("../outside.md")

    with pytest.raises(PathOutsideVaultError):
        transport.write_text(tmp_path / "absolute.md", "content")


def test_obsidian_cli_transport_nonzero_exit_raises_command_error(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliCommandError, ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "read", "vault=Vault", "path=wiki/index.md"): (2, "", "Obsidian app is not running"),
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    with pytest.raises(ObsidianCliCommandError, match="read failed"):
        transport.read_text("wiki/index.md")
```

- [ ] **Step 2: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_obsidian_cli_transport.py -q
```

Expected: multiple failures because the contract-only transport raises not-implemented errors and constructor signature lacks `executable`, `vault_selector`, and `runner`.

- [ ] **Step 3: Implement transport**

Replace `llm_wiki_core/transport/obsidian_cli.py` with:

```python
from __future__ import annotations

from pathlib import Path
import subprocess

from llm_wiki_core.transport.filesystem import PathOutsideVaultError, SearchResult, _is_relative_to
from llm_wiki_core.transport.obsidian_cli_runner import (
    ObsidianCliProfile,
    ObsidianCliRunner,
    ObsidianCliRunResult,
    SubprocessObsidianCliRunner,
)


class ObsidianCliTransportError(Exception):
    """Base error for official Obsidian CLI transport operations."""


class ObsidianCliCommandError(ObsidianCliTransportError):
    """Raised when an Obsidian CLI command exits non-zero."""


class ObsidianCliTimeoutError(ObsidianCliTransportError):
    """Raised when an Obsidian CLI command times out."""


class ObsidianCliParseError(ObsidianCliTransportError):
    """Raised when Obsidian CLI output cannot be parsed."""


class ObsidianCliTransport:
    def __init__(
        self,
        vault_root: str | Path,
        executable: str = "obsidian",
        vault_selector: str | None = None,
        runner: ObsidianCliRunner | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        self.vault_root = Path(vault_root).resolve()
        self.vault_selector = vault_selector or self.vault_root.name
        self.profile = ObsidianCliProfile(
            executable=executable,
            vault_selector=self.vault_selector,
            timeout_seconds=timeout_seconds,
        )
        self.runner = runner or SubprocessObsidianCliRunner()

    def read_text(self, relative_path: str | Path) -> str:
        path = self._normalize_vault_relative_path(relative_path)
        result = self._run("read", self.profile.read_argv(path))
        return result.stdout

    def write_text(self, relative_path: str | Path, content: str) -> str:
        path = self._normalize_vault_relative_path(relative_path)
        self._run("write", self.profile.write_argv(path, content))
        return path

    def append_text(self, relative_path: str | Path, content: str) -> str:
        path = self._normalize_vault_relative_path(relative_path)
        self._run("append", self.profile.append_argv(path, content))
        return path

    def exists(self, relative_path: str | Path) -> bool:
        path = self._normalize_vault_relative_path(relative_path)
        try:
            self._run("read", self.profile.read_argv(path))
        except ObsidianCliCommandError as error:
            message = str(error).casefold()
            if "not found" in message or "no such" in message or "missing" in message:
                return False
            raise
        return True

    def list_markdown(self, root: str | Path = "wiki") -> list[str]:
        root_path = self._normalize_vault_relative_path(root)
        result = self._run("files", self.profile.files_argv(root_path))
        paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(path for path in paths if path.lower().endswith(".md"))

    def search_text(self, query: str, root: str | Path = "wiki") -> list[SearchResult]:
        if not query:
            return []
        root_path = self._normalize_vault_relative_path(root)
        result = self._run("search", self.profile.search_argv(query, root_path))
        return _parse_search_results(result.stdout)

    def _run(self, operation: str, argv: list[str]) -> ObsidianCliRunResult:
        try:
            result = self.runner.run(argv, timeout_seconds=self.profile.timeout_seconds)
        except subprocess.TimeoutExpired as error:
            raise ObsidianCliTimeoutError(f"obsidian {operation} timed out after {self.profile.timeout_seconds}s") from error
        if result.returncode != 0:
            stderr = result.stderr.strip() or "no stderr"
            raise ObsidianCliCommandError(f"obsidian {operation} failed with exit {result.returncode}: {stderr}")
        return result

    def _normalize_vault_relative_path(self, relative_path: str | Path) -> str:
        raw_path = Path(relative_path)
        if raw_path.is_absolute():
            raise PathOutsideVaultError(f"Path must be vault-relative: {raw_path}")
        resolved = (self.vault_root / raw_path).resolve()
        if not _is_relative_to(resolved, self.vault_root):
            raise PathOutsideVaultError(f"Path resolves outside vault: {relative_path}")
        return raw_path.as_posix()


def _parse_search_results(output: str) -> list[SearchResult]:
    results: list[SearchResult] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 2)
        if len(parts) != 3:
            raise ObsidianCliParseError(f"Cannot parse search result line: {line}")
        path, line_number, text = parts
        try:
            parsed_line_number = int(line_number)
        except ValueError as error:
            raise ObsidianCliParseError(f"Cannot parse search result line number: {line}") from error
        results.append(SearchResult(path=path, line_number=parsed_line_number, line=text))
    return results
```

Update `llm_wiki_core/transport/__init__.py` imports and `__all__`:

```python
from llm_wiki_core.transport.obsidian_cli import (
    ObsidianCliCommandError,
    ObsidianCliParseError,
    ObsidianCliTimeoutError,
    ObsidianCliTransport,
    ObsidianCliTransportError,
)
```

Remove `ObsidianCliTransportNotImplementedError` from imports and `__all__`.

- [ ] **Step 4: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_obsidian_cli_transport.py tests/unit/test_obsidian_cli_command_profile.py -q
```

Expected: all tests in both files pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add llm_wiki_core/transport/obsidian_cli.py llm_wiki_core/transport/__init__.py tests/unit/test_obsidian_cli_transport.py
git commit -m "实现 Obsidian CLI 传输接口"
```

---

### Task 3: Transport Detection Snapshot And Capability Probes

**Files:**
- Modify: `llm_wiki_core/operations/detect_transport.py`
- Modify: `tests/unit/test_transport_detection.py`

**Interfaces:**
- Extends: `TransportAvailability` with:
  - `capabilities: dict[str, bool]`
  - `vault_selector: str | None`
  - `transport_kind: str`
- Extends: `detect_transport(vault_root, force=False, runner=None, which=None)`.
- Produces: official `obsidian` availability separate from legacy `obsidian-cli`.
- Produces: temporary probe path `.vault-meta/obsidian-cli-probe.md`, removed after probe.

- [ ] **Step 1: Write failing detection tests**

Append these tests to `tests/unit/test_transport_detection.py`:

```python
def test_detect_transport_records_official_obsidian_probe_failure_as_filesystem(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    class ProbeFailRunner:
        def run(self, argv: list[str], timeout_seconds: int):
            from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliRunResult

            if argv[:2] == ["obsidian", "--help"]:
                return ObsidianCliRunResult(argv, 0, "read\ncreate\nappend\nfiles\nsearch:context\n", "")
            return ObsidianCliRunResult(argv, 1, "", "Obsidian app is not running")

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        runner=ProbeFailRunner(),
        which=lambda name: "obsidian" if name == "obsidian" else None,
    )

    assert result.snapshot.preferred == "filesystem"
    assert result.snapshot.available["obsidian"].available is True
    assert result.snapshot.available["obsidian"].implemented is False
    assert result.snapshot.available["obsidian"].capabilities["read"] is False
    assert "probe failed" in result.snapshot.available["obsidian"].reason


def test_detect_transport_can_prefer_official_obsidian_after_all_probes_pass(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    class ProbePassRunner:
        def run(self, argv: list[str], timeout_seconds: int):
            from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliRunResult

            command = argv[1]
            if command == "--help":
                return ObsidianCliRunResult(argv, 0, "read\ncreate\nappend\nfiles\nsearch:context\n", "")
            if command == "read" and "path=wiki/index.md" in argv:
                return ObsidianCliRunResult(argv, 0, "# Wiki Index\n", "")
            if command == "create":
                return ObsidianCliRunResult(argv, 0, "", "")
            if command == "append":
                return ObsidianCliRunResult(argv, 0, "", "")
            if command == "read" and "path=.vault-meta/obsidian-cli-probe.md" in argv:
                return ObsidianCliRunResult(argv, 0, "llm-wiki-core obsidian probe\nappend-ok\n", "")
            if command == "files":
                return ObsidianCliRunResult(argv, 0, "wiki/index.md\n", "")
            if command == "search:context":
                return ObsidianCliRunResult(argv, 0, "wiki/index.md:1:# Wiki Index\n", "")
            return ObsidianCliRunResult(argv, 1, "", "unexpected")

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        runner=ProbePassRunner(),
        which=lambda name: "obsidian" if name == "obsidian" else None,
    )

    official = result.snapshot.available["obsidian"]
    assert result.snapshot.preferred == "obsidian"
    assert result.snapshot.fallback_chain == ["obsidian", "filesystem"]
    assert official.available is True
    assert official.implemented is True
    assert official.vault_selector == tmp_path.name
    assert official.capabilities == {
        "read": True,
        "write": True,
        "append": True,
        "list": True,
        "search": True,
    }
    assert not (tmp_path / ".vault-meta" / "obsidian-cli-probe.md").exists()


def test_detect_transport_records_legacy_obsidian_cli_as_unimplemented(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        which=lambda name: "legacy-obsidian-cli" if name == "obsidian-cli" else None,
    )

    legacy = result.snapshot.available["obsidian-cli"]
    assert result.snapshot.preferred == "filesystem"
    assert legacy.available is True
    assert legacy.implemented is False
    assert legacy.transport_kind == "legacy"
```

Update existing `test_detect_transport_records_obsidian_cli_as_available_but_unimplemented` so it asserts legacy behavior for `obsidian-cli`, not official runtime eligibility.

- [ ] **Step 2: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_transport_detection.py -q
```

Expected: failures because `detect_transport` does not accept `runner` or `which`, and snapshot availability lacks `obsidian`, `capabilities`, `vault_selector`, and `transport_kind`.

- [ ] **Step 3: Implement snapshot and probes**

Modify `TransportAvailability`:

```python
@dataclass(frozen=True)
class TransportAvailability:
    available: bool
    executable: str | None = None
    implemented: bool = False
    reason: str = ""
    capabilities: dict[str, bool] = field(default_factory=dict)
    vault_selector: str | None = None
    transport_kind: str = ""
```

Change the function signature:

```python
def detect_transport(
    vault_root: str | Path,
    force: bool = False,
    runner: object | None = None,
    which: object | None = None,
) -> TransportDetectionResult:
```

Inside `_detect_snapshot`, use:

```python
which_fn = which or shutil.which
official_executable = which_fn("obsidian")
legacy_executable = which_fn("obsidian-cli")
```

Add helper functions:

```python
REQUIRED_OBSIDIAN_CAPABILITIES = ("read", "write", "append", "list", "search")
PROBE_PATH = ".vault-meta/obsidian-cli-probe.md"
PROBE_BASE = "llm-wiki-core obsidian probe\n"
PROBE_APPEND = "append-ok\n"


def _empty_capabilities() -> dict[str, bool]:
    return {name: False for name in REQUIRED_OBSIDIAN_CAPABILITIES}


def _probe_official_obsidian(root: Path, executable: str, runner: object | None) -> tuple[bool, dict[str, bool], str, str]:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport, ObsidianCliTransportError

    vault_selector = root.name
    transport = ObsidianCliTransport(
        root,
        executable=executable,
        vault_selector=vault_selector,
        runner=runner,
    )
    capabilities = _empty_capabilities()
    try:
        index_text = transport.read_text("wiki/index.md")
        if "# Wiki Index" not in index_text:
            return False, capabilities, vault_selector, "official Obsidian CLI probe failed: wiki/index.md did not match this vault."
        capabilities["read"] = True
        transport.write_text(PROBE_PATH, PROBE_BASE)
        capabilities["write"] = True
        transport.append_text(PROBE_PATH, PROBE_APPEND)
        capabilities["append"] = True
        probe_text = transport.read_text(PROBE_PATH)
        if PROBE_BASE not in probe_text or PROBE_APPEND.strip() not in probe_text:
            return False, capabilities, vault_selector, "official Obsidian CLI probe failed: write/append round trip mismatch."
        markdown_files = transport.list_markdown("wiki")
        capabilities["list"] = "wiki/index.md" in markdown_files
        search_results = transport.search_text("Wiki", "wiki")
        capabilities["search"] = bool(search_results)
    except ObsidianCliTransportError as error:
        return False, capabilities, vault_selector, f"official Obsidian CLI probe failed: {error}"
    finally:
        probe_file = root / PROBE_PATH
        if probe_file.exists():
            probe_file.unlink()
    implemented = all(capabilities.values())
    reason = "official Obsidian CLI verified for this vault." if implemented else "official Obsidian CLI probe failed: one or more capabilities were unavailable."
    return implemented, capabilities, vault_selector, reason
```

Update `_snapshot_to_json` and `_load_snapshot` to round-trip `capabilities`, `vault_selector`, and `transport_kind`.

- [ ] **Step 4: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_transport_detection.py -q
```

Expected: all transport detection tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add llm_wiki_core/operations/detect_transport.py tests/unit/test_transport_detection.py
git commit -m "增强 Obsidian CLI 探测快照"
```

---

### Task 4: Capability-Aware Runtime Selection

**Files:**
- Modify: `llm_wiki_core/transport/runtime.py`
- Modify: `tests/unit/test_runtime_transport_selection.py`

**Interfaces:**
- Consumes: snapshot `preferred`, `available.obsidian.implemented`, `available.obsidian.capabilities`, `available.obsidian.executable`, `available.obsidian.vault_selector`.
- Produces: `RuntimeTransportSelection.transport` may be `FilesystemTransport` or `ObsidianCliTransport`.
- Produces: fallback warnings for unavailable, unimplemented, legacy, unknown, and capability-incomplete transports.

- [ ] **Step 1: Write failing runtime selector tests**

Append to `tests/unit/test_runtime_transport_selection.py`:

```python
def test_runtime_transport_selects_verified_official_obsidian_snapshot(tmp_path) -> None:
    import json
    from llm_wiki_core.transport import ObsidianCliTransport, select_runtime_transport

    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "preferred": "obsidian",
                "fallback_chain": ["obsidian", "filesystem"],
                "available": {
                    "obsidian": {
                        "available": True,
                        "implemented": True,
                        "executable": "obsidian",
                        "vault_selector": "Vault",
                        "capabilities": {
                            "read": True,
                            "write": True,
                            "append": True,
                            "list": True,
                            "search": True,
                        },
                    },
                    "filesystem": {"available": True, "implemented": True},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "obsidian"
    assert isinstance(selection.transport, ObsidianCliTransport)
    assert selection.warnings == []


def test_runtime_transport_falls_back_when_obsidian_capabilities_are_incomplete(tmp_path) -> None:
    import json
    from llm_wiki_core.transport import FilesystemTransport, select_runtime_transport

    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "preferred": "obsidian",
                "available": {
                    "obsidian": {
                        "available": True,
                        "implemented": True,
                        "executable": "obsidian",
                        "vault_selector": "Vault",
                        "capabilities": {
                            "read": True,
                            "write": True,
                            "append": False,
                            "list": True,
                            "search": True,
                        },
                    },
                    "filesystem": {"available": True, "implemented": True},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "filesystem"
    assert isinstance(selection.transport, FilesystemTransport)
    assert any("missing required capabilities" in warning for warning in selection.warnings)


def test_runtime_transport_falls_back_from_legacy_obsidian_cli_snapshot(tmp_path) -> None:
    import json
    from llm_wiki_core.transport import select_runtime_transport

    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "preferred": "obsidian-cli",
                "available": {
                    "obsidian-cli": {
                        "available": True,
                        "implemented": False,
                        "transport_kind": "legacy",
                    },
                    "filesystem": {"available": True, "implemented": True},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "filesystem"
    assert any("legacy" in warning for warning in selection.warnings)
```

- [ ] **Step 2: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_runtime_transport_selection.py -q
```

Expected: verified official snapshot still selects filesystem; capability and legacy warning assertions fail.

- [ ] **Step 3: Implement selector**

Modify `RuntimeTransportSelection` annotation:

```python
transport: object
```

Import:

```python
from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport
```

Add:

```python
REQUIRED_OBSIDIAN_CAPABILITIES = ("read", "write", "append", "list", "search")
```

In `select_runtime_transport`, after loading snapshot:

```python
if preferred_name == "obsidian":
    obsidian = _obsidian_transport_from_snapshot(root, snapshot)
    if isinstance(obsidian, RuntimeTransportSelection):
        return obsidian
```

Add helper:

```python
def _obsidian_transport_from_snapshot(root: Path, snapshot: dict[str, object]) -> RuntimeTransportSelection | list[str]:
    available = snapshot.get("available", {})
    if not isinstance(available, dict):
        return ["Preferred transport 'obsidian' has no availability metadata; using filesystem."]
    metadata = available.get("obsidian", {})
    if not isinstance(metadata, dict):
        return ["Preferred transport 'obsidian' has invalid metadata; using filesystem."]
    if not bool(metadata.get("available", False)):
        return ["Preferred transport 'obsidian' is not available; using filesystem."]
    if not bool(metadata.get("implemented", False)):
        return ["Preferred transport 'obsidian' is not implemented; using filesystem."]
    capabilities = metadata.get("capabilities", {})
    if not isinstance(capabilities, dict) or not all(bool(capabilities.get(name)) for name in REQUIRED_OBSIDIAN_CAPABILITIES):
        return ["Preferred transport 'obsidian' is missing required capabilities; using filesystem."]
    executable = metadata.get("executable")
    vault_selector = metadata.get("vault_selector")
    if not isinstance(executable, str) or not executable:
        return ["Preferred transport 'obsidian' has no executable metadata; using filesystem."]
    if not isinstance(vault_selector, str) or not vault_selector:
        return ["Preferred transport 'obsidian' has no vault selector metadata; using filesystem."]
    return RuntimeTransportSelection(
        name="obsidian",
        transport=ObsidianCliTransport(root, executable=executable, vault_selector=vault_selector),
        snapshot_preferred="obsidian",
    )
```

Use the helper result:

```python
obsidian_result = _obsidian_transport_from_snapshot(root, snapshot)
if isinstance(obsidian_result, RuntimeTransportSelection):
    return obsidian_result
warnings = obsidian_result
```

Update `_warnings_for_snapshot` for `obsidian-cli`:

```python
if preferred_name == "obsidian-cli":
    return ["Preferred transport 'obsidian-cli' is a legacy CLI and is not implemented by R2; using filesystem."]
```

- [ ] **Step 4: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_runtime_transport_selection.py -q
```

Expected: runtime selector tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add llm_wiki_core/transport/runtime.py tests/unit/test_runtime_transport_selection.py
git commit -m "启用能力感知的运行通道选择"
```

---

### Task 5: Human-Readable Warning Output

**Files:**
- Modify: `llm_wiki_core/cli.py`
- Modify: `tests/unit/test_status_continue_operations.py`

**Interfaces:**
- Consumes: result dataclasses with `warnings: list[str]`.
- Produces: text CLI output that includes a `warnings:` block when warnings exist.

- [ ] **Step 1: Write failing warning-output tests**

Append to `tests/unit/test_status_continue_operations.py`:

```python
def test_cli_status_prints_transport_warnings(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI status warnings")
    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        '{"preferred": "obsidian-cli", "available": {"obsidian-cli": {"available": true, "implemented": false}, "filesystem": {"available": true, "implemented": true}}}\n',
        encoding="utf-8",
    )

    exit_code = main(["status", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "warnings:" in output
    assert "obsidian-cli" in output


def test_cli_continue_prints_transport_warnings(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI continue warnings")
    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        '{"preferred": "obsidian-cli", "available": {"obsidian-cli": {"available": true, "implemented": false}, "filesystem": {"available": true, "implemented": true}}}\n',
        encoding="utf-8",
    )

    exit_code = main(["continue", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "warnings:" in output
    assert "obsidian-cli" in output
```

- [ ] **Step 2: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_status_continue_operations.py -q
```

Expected: warning-output tests fail because text output currently omits warnings.

- [ ] **Step 3: Implement warning printer**

Add helper in `llm_wiki_core/cli.py`:

```python
def _print_warnings(result: object) -> None:
    warnings = getattr(result, "warnings", [])
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
```

Call `_print_warnings(result)` in the `detect-transport`, `status`, and `continue` branches after command-specific details and before `next:`.

- [ ] **Step 4: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_status_continue_operations.py -q
```

Expected: status and continue tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add llm_wiki_core/cli.py tests/unit/test_status_continue_operations.py
git commit -m "显示传输通道回退警告"
```

---

### Task 6: R2 Documentation And Documentation Tests

**Files:**
- Create: `tests/unit/test_r2_obsidian_cli_docs.py`
- Create: `docs/r2-obsidian-cli-transport-report.md`
- Modify: `docs/transport-contract.md`
- Modify: `docs/roadmap-schedule.md`
- Modify: `docs/user-guide.md`
- Modify: `README.md` if the docs test requires front-page visibility.

**Interfaces:**
- Consumes: completed R2 behavior and design.
- Produces: public documentation of official CLI boundary, legacy CLI boundary, and fallback behavior.

- [ ] **Step 1: Write failing docs test**

Create `tests/unit/test_r2_obsidian_cli_docs.py`:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_transport_contract_documents_official_and_legacy_obsidian_cli() -> None:
    contract = _read("docs/transport-contract.md")

    assert "official `obsidian` CLI" in contract
    assert "legacy `obsidian-cli`" in contract
    assert "capability probe" in contract
    assert "filesystem fallback" in contract


def test_r2_report_documents_verified_boundary() -> None:
    report = _read("docs/r2-obsidian-cli-transport-report.md")

    assert "# R2 Obsidian CLI Transport Report" in report
    assert "Status: complete" in report
    assert "official `obsidian`" in report
    assert "legacy `obsidian-cli`" in report
    assert "fake runner" in report


def test_user_guide_documents_obsidian_cli_setup_without_requiring_it() -> None:
    guide = _read("docs/user-guide.md")

    assert "Obsidian CLI" in guide
    assert "filesystem fallback" in guide
    assert "not required" in guide
```

- [ ] **Step 2: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_r2_obsidian_cli_docs.py -q
```

Expected: fails because the R2 report does not exist and docs do not contain the required R2 terms.

- [ ] **Step 3: Update docs**

Update `docs/transport-contract.md` with an R2 section:

```markdown
## R2 Official Obsidian CLI Runtime Eligibility

R2 distinguishes the official `obsidian` CLI from the legacy `obsidian-cli` command.

The official `obsidian` CLI can become runtime eligible only after detection verifies vault binding and read/write/append/list/search capability probes. The legacy `obsidian-cli` command is recorded as legacy metadata and remains unimplemented in R2.

If the official CLI is missing, disabled, bound to the wrong vault, missing a capability, or returns a probe error, the runtime selector uses filesystem fallback.
```

Create `docs/r2-obsidian-cli-transport-report.md`:

```markdown
# R2 Obsidian CLI Transport Report

Date: 2026-06-26

Status: complete.

R2 adds a conservative official `obsidian` CLI transport path for local desktop workflows. The official CLI is runtime eligible only after vault binding and read/write/append/list/search capability probes pass.

The legacy `obsidian-cli` command is still detected as legacy metadata, but it is not used by the R2 runtime.

Automated verification uses a fake runner so tests do not require Obsidian to be installed, running, or configured. Filesystem fallback remains the safe path in all unverified cases.
```

Update `docs/user-guide.md` with:

```markdown
## Optional Obsidian CLI Runtime

Obsidian CLI is not required. The default portable path remains filesystem fallback.

When the official `obsidian` CLI is installed, enabled in Obsidian, and verified against the target vault, `llm-wiki-core` may use it for read/write/append/list/search. If verification fails, commands continue through filesystem fallback.

The legacy `obsidian-cli` command is not used as an R2 runtime transport.
```

Update `docs/roadmap-schedule.md` R2 status after implementation is complete.

- [ ] **Step 4: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_r2_obsidian_cli_docs.py -q
```

Expected: docs tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add docs/transport-contract.md docs/roadmap-schedule.md docs/user-guide.md docs/r2-obsidian-cli-transport-report.md tests/unit/test_r2_obsidian_cli_docs.py README.md
git commit -m "补充 R2 Obsidian CLI 文档"
```

If `README.md` is unchanged, omit it from `git add`.

---

### Task 7: Final Verification, Progress Record, Merge, And Push

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: all R2 implementation commits.
- Produces: verified R2 completion record and remote `main` update.

- [ ] **Step 1: Run focused R2 tests**

Run:

```powershell
python -m pytest tests/unit/test_obsidian_cli_command_profile.py tests/unit/test_obsidian_cli_transport.py tests/unit/test_transport_detection.py tests/unit/test_runtime_transport_selection.py tests/unit/test_status_continue_operations.py tests/unit/test_r2_obsidian_cli_docs.py -q
```

Expected: all focused R2 tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with the existing Windows POSIX shell dry-run skip still acceptable.

- [ ] **Step 3: Verify reference repo untouched**

Run:

```powershell
git -C D:\ai\llmWiki\claude-obsidian status --short --branch
```

Expected:

```text
## main...origin/main
```

- [ ] **Step 4: Clean test cache**

Run:

```powershell
if (Test-Path -LiteralPath .pytest_cache) {
  $root = (Resolve-Path -LiteralPath .).Path
  $target = (Resolve-Path -LiteralPath .pytest_cache).Path
  if (-not $target.StartsWith($root)) { throw "Refusing to remove path outside repo: $target" }
  Remove-Item -LiteralPath $target -Recurse -Force
}
```

- [ ] **Step 5: Update progress document**

Append a new stage to `D:/ai/llmWiki/codex_doc/project_understanding_progress.md` with:

```markdown
## 阶段 59：R2 Obsidian CLI Transport 实现

状态：已完成

### 本阶段目标

实现官方 `obsidian` CLI transport 的保守运行路径，同时保持 filesystem fallback。

### 验证结果

- Focused R2 tests：记录实际 pass 数。
- Full suite：记录实际 pass/skip 数。
- `claude-obsidian`：确认无修改。
- `v0.1.0-mvp` tag：确认未移动。

### Git 结果

- R2 branch：`r2-obsidian-cli-transport`
- Final commit：记录实际 commit。
- Remote main：记录实际 hash。
```

- [ ] **Step 6: Commit any final docs or progress-related repo docs**

If repo files changed after Task 6, commit them:

```powershell
git add <changed-repo-files>
git commit -m "完成 R2 验证文档收尾"
```

Do not add `D:/ai/llmWiki/codex_doc/project_understanding_progress.md` to `llm-wiki-core`; it lives outside the repo.

- [ ] **Step 7: Merge to main and push**

Run:

```powershell
git checkout main
git pull --ff-only
git merge --ff-only r2-obsidian-cli-transport
python -m pytest -q
git push origin main
git branch -d r2-obsidian-cli-transport
```

Expected:

- merge is fast-forward;
- post-merge tests pass;
- `origin/main` advances to the R2 final commit;
- local R2 branch is deleted after merge.

- [ ] **Step 8: Final status checks**

Run:

```powershell
git status --short --branch
git log --oneline --decorate -5
git ls-remote --heads --tags origin
git -C D:\ai\llmWiki\claude-obsidian status --short --branch
```

Expected:

- `llm-wiki-core` is clean on `main...origin/main`;
- `claude-obsidian` is clean;
- `refs/heads/main` points to the R2 final commit;
- `refs/tags/v0.1.0-mvp^{}` still points to the original MVP commit.
