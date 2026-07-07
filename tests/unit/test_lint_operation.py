from __future__ import annotations


def test_lint_fresh_vault_has_no_blockers(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Lint fresh vault")

    result = lint_wiki(tmp_path)

    assert result.operation == "lint"
    assert result.status == "success"
    assert result.counts["blocker"] == 0
    assert result.counts["high"] == 0
    assert result.report_path is not None
    assert (tmp_path / result.report_path).is_file()


def test_lint_reports_invalid_manifest_as_blocker(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Broken manifest")
    (tmp_path / ".raw" / ".manifest.json").write_text("{not json", encoding="utf-8")

    result = lint_wiki(tmp_path, write_report=False)

    assert result.counts["blocker"] == 1
    assert any(finding.check == "manifest-json" for finding in result.findings)


def test_lint_reports_missing_frontmatter_dead_link_and_orphan(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Broken page")
    page = tmp_path / "wiki" / "concepts" / "Broken Page.md"
    page.write_text("# Broken Page\n\nLinks to [[Missing Page]].\n", encoding="utf-8")

    result = lint_wiki(tmp_path, write_report=False)

    checks = {finding.check for finding in result.findings}
    assert "frontmatter" in checks
    assert "dead-wikilink" in checks
    assert "orphan-page" in checks


def test_lint_reports_missing_required_frontmatter_fields(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Missing frontmatter fields")
    page = tmp_path / "wiki" / "concepts" / "Incomplete Frontmatter.md"
    page.write_text(
        "---\n"
        "type: concept\n"
        'title: "Incomplete Frontmatter"\n'
        "---\n"
        "\n"
        "# Incomplete Frontmatter\n",
        encoding="utf-8",
    )

    result = lint_wiki(tmp_path, write_report=False)

    missing = {
        finding.message
        for finding in result.findings
        if finding.check == "frontmatter-field" and finding.path == "wiki/concepts/Incomplete Frontmatter.md"
    }
    assert "Frontmatter missing required field: created." in missing
    assert "Frontmatter missing required field: updated." in missing
    assert "Frontmatter missing required field: status." in missing


def test_lint_reports_malformed_frontmatter_delimiter(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Malformed frontmatter")
    page = tmp_path / "wiki" / "concepts" / "Malformed Frontmatter.md"
    page.write_text(
        "---\n"
        "type: concept\n"
        'title: "Malformed Frontmatter"\n'
        "\n"
        "# Malformed Frontmatter\n",
        encoding="utf-8",
    )

    result = lint_wiki(tmp_path, write_report=False)

    assert any(
        finding.check == "frontmatter"
        and finding.path == "wiki/concepts/Malformed Frontmatter.md"
        and "closing delimiter" in finding.message
        for finding in result.findings
    )


def test_lint_wiki_uses_transport_for_reads_and_report_writes(tmp_path) -> None:
    from llm_wiki_core.operations.lint import lint_wiki

    class SpyTransport:
        def __init__(self) -> None:
            self.exists_paths: list[str] = []
            self.read_paths: list[str] = []
            self.list_roots: list[str] = []
            self.write_calls: list[tuple[str, str]] = []
            self.existing = {
                ".raw/.manifest.json",
                "wiki/index.md",
                "wiki/log.md",
                "wiki/hot.md",
                "wiki/overview.md",
                "wiki/sources",
                "wiki/entities",
                "wiki/concepts",
                "wiki/questions",
                "wiki/comparisons",
                "wiki/meta",
                "wiki/concepts/Broken Page.md",
            }
            self.files = {
                ".raw/.manifest.json": '{"schema_version": 1, "sources": {}}\n',
                "wiki/concepts/Broken Page.md": "# Broken Page\n\nLinks to [[Missing Page]].\n",
            }

        def exists(self, relative_path: str) -> bool:
            self.exists_paths.append(relative_path)
            return relative_path in self.existing

        def read_text(self, relative_path: str) -> str:
            self.read_paths.append(relative_path)
            return self.files[relative_path]

        def list_markdown(self, root: str = "wiki") -> list[str]:
            self.list_roots.append(root)
            return ["wiki/concepts/Broken Page.md"]

        def write_text(self, relative_path: str, content: str) -> str:
            self.write_calls.append((relative_path, content))
            return relative_path

    transport = SpyTransport()

    result = lint_wiki(tmp_path, transport=transport)

    assert result.status == "success"
    checks = {finding.check for finding in result.findings}
    assert {"frontmatter", "dead-wikilink", "orphan-page"}.issubset(checks)
    assert ".raw/.manifest.json" in transport.exists_paths
    assert ".raw/.manifest.json" in transport.read_paths
    assert "wiki" in transport.list_roots
    assert "wiki/concepts/Broken Page.md" in transport.read_paths
    assert transport.write_calls
    assert transport.write_calls[0][0].startswith("wiki/meta/lint-report-")
    assert result.report_path == transport.write_calls[0][0]


def test_cli_lint_prints_summary_and_writes_report(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI lint")

    exit_code = main(["lint", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "lint success" in output
    assert "blocker: 0" in output
    assert list((tmp_path / "wiki" / "meta").glob("lint-report-*.md"))


def test_lint_accepts_file_and_url_manifest_source_types(tmp_path) -> None:
    import json

    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Lint URL manifest")
    manifest_path = tmp_path / ".raw" / ".manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"] = {
        "articles/file.md": {
            "source_path": ".raw/articles/file.md",
            "source_type": "file",
            "status": "ingested",
            "content_fingerprint": "sha256:file",
            "generated_pages": [],
            "updated_pages": [],
        },
        "url/2026-06-30/example/snapshot/source.md": {
            "source_path": ".raw/url/2026-06-30/example/snapshot/source.md",
            "source_type": "url",
            "status": "ingested",
            "content_fingerprint": "sha256:url",
            "source_url": "https://example.com/source",
            "fetched_at": "2026-06-30T01:02:03+08:00",
            "http_status": 200,
            "content_type": "text/html; charset=utf-8",
            "raw_snapshot_path": ".raw/url/2026-06-30/example/snapshot/response.html",
            "generated_pages": [],
            "updated_pages": [],
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = lint_wiki(tmp_path, write_report=False)

    assert not [finding for finding in result.findings if finding.check == "manifest-source-type"]


def test_lint_rejects_unsupported_manifest_source_type(tmp_path) -> None:
    import json

    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Lint invalid source type")
    manifest_path = tmp_path / ".raw" / ".manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"] = {
        "remote/example.md": {
            "source_path": ".raw/remote/example.md",
            "source_type": "remote",
            "status": "ingested",
            "content_fingerprint": "sha256:remote",
            "generated_pages": [],
            "updated_pages": [],
        }
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = lint_wiki(tmp_path, write_report=False)

    assert any(
        finding.check == "manifest-source-type"
        and finding.severity == "blocker"
        and "remote" in finding.message
        for finding in result.findings
    )


def test_lint_rejects_missing_or_empty_manifest_content_fingerprint(tmp_path) -> None:
    import json

    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki

    init_vault(tmp_path, purpose="Lint missing fingerprint")
    manifest_path = tmp_path / ".raw" / ".manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"] = {
        "articles/missing.md": {
            "source_path": ".raw/articles/missing.md",
            "source_type": "file",
            "status": "ingested",
            "generated_pages": [],
            "updated_pages": [],
        },
        "articles/empty.md": {
            "source_path": ".raw/articles/empty.md",
            "source_type": "file",
            "status": "ingested",
            "content_fingerprint": "",
            "generated_pages": [],
            "updated_pages": [],
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = lint_wiki(tmp_path, write_report=False)

    findings = [finding for finding in result.findings if finding.check == "manifest-content-fingerprint"]
    assert len(findings) == 2
    assert all(finding.severity == "blocker" for finding in findings)


def test_lint_required_paths_come_from_organization_definition(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations import lint as lint_module
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Lint organization contract")

    monkeypatch.setattr(
        lint_module,
        "required_paths_for_organization",
        lambda name="generic": ("wiki/missing-from-organization-contract",),
    )

    result = lint_module.lint_wiki(tmp_path, write_report=False)

    assert any(
        finding.check == "required-path"
        and finding.path == "wiki/missing-from-organization-contract"
        for finding in result.findings
    )
