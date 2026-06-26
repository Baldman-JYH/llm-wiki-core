from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run_module(module: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def _assert_success(result: subprocess.CompletedProcess[str]) -> str:
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_python_module_entrypoints_expose_cli_version() -> None:
    package_result = _run_module("llm_wiki_core", "--version")
    package_output = _assert_success(package_result)
    assert "llm-wiki-core 0.1.0" in package_output

    cli_result = _run_module("llm_wiki_core.cli", "--version")
    cli_output = _assert_success(cli_result)
    assert "llm-wiki-core 0.1.0" in cli_output


def test_python_module_cli_runs_documented_local_workflow(tmp_path) -> None:
    vault = tmp_path / "vault"

    init_output = _assert_success(
        _run_module(
            "llm_wiki_core",
            "init",
            str(vault),
            "--purpose",
            "Subprocess CLI artifact workflow.",
        )
    )
    assert "init success" in init_output
    assert (vault / "AGENTS.md").is_file()

    transport_output = _assert_success(_run_module("llm_wiki_core", "detect-transport", str(vault), "--force"))
    assert "detect-transport success" in transport_output
    snapshot = json.loads((vault / ".vault-meta" / "transport.json").read_text(encoding="utf-8"))
    assert snapshot["preferred"] == "filesystem"

    source = vault / ".raw" / "articles" / "karpathy-llm-wiki.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "# Karpathy LLM Wiki\n\n"
        "The durable artifact is a Markdown Wiki with raw sources, metadata, links, logs, and hot context.",
        encoding="utf-8",
    )

    ingest_output = _assert_success(
        _run_module("llm_wiki_core", "ingest", str(vault), ".raw/articles/karpathy-llm-wiki.md")
    )
    assert "ingest success" in ingest_output
    assert (vault / "wiki" / "sources" / "Karpathy Llm Wiki.md").is_file()

    status_output = _assert_success(_run_module("llm_wiki_core", "status", str(vault)))
    assert "status success" in status_output
    assert "preferred transport: filesystem" in status_output

    continue_output = _assert_success(_run_module("llm_wiki_core", "continue", str(vault)))
    assert "continue success" in continue_output
    assert "files read: 3" in continue_output

    query_output = _assert_success(_run_module("llm_wiki_core", "query", str(vault), "Karpathy LLM Wiki"))
    assert "query success" in query_output
    assert "[[Karpathy Llm Wiki]]" in query_output

    save_output = _assert_success(
        _run_module(
            "llm_wiki_core",
            "save",
            str(vault),
            "--title",
            "Subprocess CLI",
            "--content",
            "Subprocess CLI verification protects the actual local command path.",
        )
    )
    assert "save success" in save_output
    assert (vault / "wiki" / "questions" / "Subprocess CLI.md").is_file()

    lint_output = _assert_success(_run_module("llm_wiki_core", "lint", str(vault)))
    assert "lint success" in lint_output
    assert "blocker: 0" in lint_output
    assert "high: 0" in lint_output
