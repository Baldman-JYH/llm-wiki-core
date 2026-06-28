from __future__ import annotations

import json


def _last_json(stdout: str) -> dict[str, object]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    assert lines
    return json.loads(lines[-1])


def test_cli_ingest_batch_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI batch")
    articles = tmp_path / ".raw" / "articles"
    articles.mkdir(parents=True)
    (articles / "one.md").write_text("# One\n\nFirst.", encoding="utf-8")
    (articles / "two.md").write_text("# Two\n\nSecond.", encoding="utf-8")

    exit_code = main(["ingest-batch", str(tmp_path), ".raw/articles"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ingest-batch success" in output
    assert "root: .raw/articles" in output
    assert "total: 2" in output
    assert "succeeded: 2" in output
    assert "skipped: 0" in output
    assert "failed: 0" in output
    assert "next: Query the wiki, lint the vault, or ingest another batch." in output


def test_cli_ingest_batch_json_includes_items(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI batch JSON")
    articles = tmp_path / ".raw" / "articles"
    articles.mkdir(parents=True)
    (articles / "example.md").write_text("# Example\n\nJSON.", encoding="utf-8")

    exit_code = main(["ingest-batch", str(tmp_path), ".raw/articles", "--json"])

    assert exit_code == 0
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "ingest-batch"
    assert payload["status"] == "success"
    assert payload["root_path"] == ".raw/articles"
    assert payload["total"] == 1
    assert payload["succeeded"] == 1
    assert payload["failed"] == 0
    items = payload["items"]
    assert isinstance(items, list)
    assert items[0]["source_path"] == ".raw/articles/example.md"
    assert items[0]["status"] == "success"


def test_cli_ingest_batch_invalid_root_returns_error_exit_code(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI batch error")

    exit_code = main(["ingest-batch", str(tmp_path), "notes"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "ingest-batch error" in captured.err
    assert ".raw/" in captured.err


def test_cli_ingest_batch_prints_failed_items(monkeypatch, tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.ingest_batch import BatchIngestItem, BatchIngestResult

    def fake_ingest_batch(vault_root: str, source_root: str, force: bool = False) -> BatchIngestResult:
        return BatchIngestResult(
            operation="ingest-batch",
            status="partial",
            root_path=source_root,
            total=2,
            succeeded=1,
            skipped=0,
            failed=1,
            items=[
                BatchIngestItem(source_path=".raw/articles/ok.md", status="success"),
                BatchIngestItem(
                    source_path=".raw/articles/broken.md",
                    status="failed",
                    error_type="ValueError",
                    error_message="cannot read source",
                ),
            ],
            next_suggested_action="Query the wiki, lint the vault, or ingest another batch.",
        )

    monkeypatch.setattr("llm_wiki_core.cli.ingest_batch", fake_ingest_batch)

    exit_code = main(["ingest-batch", str(tmp_path), ".raw/articles"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ingest-batch partial" in output
    assert "failed items:" in output
    assert "- .raw/articles/broken.md: ValueError: cannot read source" in output
