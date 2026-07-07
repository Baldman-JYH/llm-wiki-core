from __future__ import annotations

import json


def test_init_vault_creates_generic_wiki_structure(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault

    result = init_vault(tmp_path, purpose="Map an example codebase")

    assert result.operation == "init"
    assert result.status == "success"
    assert (tmp_path / ".raw" / ".manifest.json").is_file()
    assert (tmp_path / "wiki" / "index.md").is_file()
    assert (tmp_path / "wiki" / "log.md").is_file()
    assert (tmp_path / "wiki" / "hot.md").is_file()
    assert (tmp_path / "wiki" / "overview.md").is_file()
    assert (tmp_path / "wiki" / "sources").is_dir()
    assert (tmp_path / "wiki" / "entities" / "_index.md").is_file()
    assert (tmp_path / "wiki" / "concepts" / "_index.md").is_file()
    assert (tmp_path / "wiki" / "questions").is_dir()
    assert (tmp_path / "wiki" / "comparisons").is_dir()
    assert (tmp_path / "wiki" / "meta").is_dir()
    assert (tmp_path / "AGENTS.md").is_file()


def test_init_vault_writes_manifest_and_seed_frontmatter(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Research local LLM wiki workflows")

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["sources"] == {}
    assert isinstance(manifest["updated"], str)

    hot = (tmp_path / "wiki" / "hot.md").read_text(encoding="utf-8")
    index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    overview = (tmp_path / "wiki" / "overview.md").read_text(encoding="utf-8")

    assert hot.startswith("---\ntype: meta\n")
    assert index.startswith("---\ntype: meta\n")
    assert overview.startswith("---\ntype: overview\n")
    assert "Research local LLM wiki workflows" in overview


def test_init_vault_does_not_overwrite_existing_files(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault

    existing = tmp_path / "wiki" / "index.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("custom index", encoding="utf-8")

    result = init_vault(tmp_path, purpose="Keep existing notes")

    assert existing.read_text(encoding="utf-8") == "custom index"
    assert "wiki/index.md" in result.files_skipped
    assert result.status == "success"


def test_init_writes_codex_agents_with_command_discovery(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Codex adapter discovery")

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    for command in [
        "llm-wiki status",
        "llm-wiki continue",
        "llm-wiki ingest",
        "llm-wiki query",
        "llm-wiki save",
        "llm-wiki lint",
    ]:
        assert command in agents
    for trigger in ["set up wiki", "check wiki status", "resume wiki context"]:
        assert trigger in agents
    assert "artifact-level equivalence" in agents


def test_cli_init_creates_vault_and_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    exit_code = main(["init", str(tmp_path), "--purpose", "Codex CLI wiki"])

    assert exit_code == 0
    assert (tmp_path / ".raw" / ".manifest.json").is_file()
    assert (tmp_path / "AGENTS.md").is_file()
    output = capsys.readouterr().out
    assert "init success" in output
    assert "next:" in output


def test_init_vault_accepts_explicit_generic_organization(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault

    result = init_vault(
        tmp_path,
        purpose="Map organization foundations",
        organization="generic",
    )

    assert result.organization == "generic"
    assert (tmp_path / "wiki" / "comparisons").is_dir()
    assert (tmp_path / "wiki" / "overview.md").is_file()


def test_init_vault_rejects_unsupported_organization_without_scaffold(tmp_path) -> None:
    import pytest

    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.vault.scaffold import UnsupportedOrganizationMode

    with pytest.raises(UnsupportedOrganizationMode):
        init_vault(tmp_path, purpose="No unsupported modes", organization="para")

    assert not (tmp_path / ".raw").exists()
    assert not (tmp_path / "wiki").exists()


def test_cli_init_accepts_explicit_generic_organization_json(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    exit_code = main(
        [
            "init",
            str(tmp_path),
            "--purpose",
            "Codex CLI organization wiki",
            "--organization",
            "generic",
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "init"
    assert payload["status"] == "success"
    assert payload["organization"] == "generic"


def test_cli_init_rejects_unsupported_organization_json_without_scaffold(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    exit_code = main(
        [
            "init",
            str(tmp_path),
            "--purpose",
            "Reject unsupported organization",
            "--organization",
            "zettelkasten",
            "--json",
        ]
    )

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "init"
    assert payload["status"] == "error"
    assert payload["error"]["type"] == "UnsupportedOrganizationMode"
    assert "Unsupported organization mode: zettelkasten" in payload["error"]["message"]
    assert not (tmp_path / ".raw").exists()
    assert not (tmp_path / "wiki").exists()
