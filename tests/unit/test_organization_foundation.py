from __future__ import annotations

import re

import pytest


def test_build_frontmatter_writes_minimum_flat_yaml_fields() -> None:
    from llm_wiki_core.schema.frontmatter import build_frontmatter

    text = build_frontmatter(
        page_type="concept",
        title="LLM Wiki Pattern",
        created="2026-07-07",
        updated="2026-07-07T08:09:10+08:00",
    )

    assert text == (
        "---\n"
        "type: concept\n"
        'title: "LLM Wiki Pattern"\n'
        "created: 2026-07-07\n"
        "updated: 2026-07-07T08:09:10+08:00\n"
        "status: seed\n"
        "---\n\n"
    )


def test_generic_organization_definition_matches_mvp_structure() -> None:
    from llm_wiki_core.vault.scaffold import get_organization_definition

    definition = get_organization_definition("generic")

    assert definition.name == "generic"
    assert ".raw" in definition.required_directories
    assert "wiki/sources" in definition.required_directories
    assert "wiki/entities" in definition.required_directories
    assert "wiki/concepts" in definition.required_directories
    assert "wiki/questions" in definition.required_directories
    assert "wiki/comparisons" in definition.required_directories
    assert "wiki/meta" in definition.required_directories
    assert definition.page_type_routes["source"] == "wiki/sources"
    assert definition.page_type_routes["entity"] == "wiki/entities"
    assert definition.page_type_routes["concept"] == "wiki/concepts"
    assert definition.page_type_routes["question"] == "wiki/questions"
    assert definition.page_type_routes["comparison"] == "wiki/comparisons"
    assert definition.page_type_routes["overview"] == "wiki/overview.md"
    assert definition.search_page_types == (
        "source",
        "concept",
        "entity",
        "question",
        "comparison",
    )

    seed_paths = {page.relative_path for page in definition.seed_pages}
    assert {
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md",
        "wiki/overview.md",
        "wiki/entities/_index.md",
        "wiki/concepts/_index.md",
    }.issubset(seed_paths)


def _normalize_dynamic_frontmatter(text: str) -> str:
    normalized = re.sub(r"^created: .*$", "created: <dynamic>", text, flags=re.MULTILINE)
    return re.sub(r"^updated: .*$", "updated: <dynamic>", normalized, flags=re.MULTILINE)


def test_generic_seed_pages_render_match_init_vault_outputs(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.vault.scaffold import get_organization_definition

    purpose = "Map an example codebase"
    init_vault(tmp_path, purpose=purpose)

    definition = get_organization_definition("generic")
    actual_pages = {
        "wiki/index.md": (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8"),
        "wiki/log.md": (tmp_path / "wiki" / "log.md").read_text(encoding="utf-8"),
        "wiki/hot.md": (tmp_path / "wiki" / "hot.md").read_text(encoding="utf-8"),
        "wiki/overview.md": (tmp_path / "wiki" / "overview.md").read_text(encoding="utf-8"),
        "wiki/entities/_index.md": (tmp_path / "wiki" / "entities" / "_index.md").read_text(encoding="utf-8"),
        "wiki/concepts/_index.md": (tmp_path / "wiki" / "concepts" / "_index.md").read_text(encoding="utf-8"),
    }

    for relative_path, actual_text in actual_pages.items():
        page = next(page for page in definition.seed_pages if page.relative_path == relative_path)
        expected_text = page.render(
            created="2026-07-07",
            updated="2026-07-07T08:09:10+08:00",
            purpose=purpose,
        )
        assert _normalize_dynamic_frontmatter(actual_text) == _normalize_dynamic_frontmatter(
            expected_text
        )


def test_init_module_no_longer_exposes_seed_page_compat_helpers() -> None:
    from llm_wiki_core.operations import init as init_module

    for helper_name in (
        "_index_page",
        "_log_page",
        "_hot_page",
        "_overview_page",
        "_sub_index_page",
    ):
        assert not hasattr(init_module, helper_name)


def test_required_paths_for_generic_organization_match_current_lint_contract() -> None:
    from llm_wiki_core.vault.scaffold import required_paths_for_organization

    paths = required_paths_for_organization("generic")

    assert paths == (
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
    )


def test_required_paths_findings_match_lint_contract() -> None:
    from llm_wiki_core.operations.lint import _check_required_paths
    from llm_wiki_core.vault.scaffold import required_paths_for_organization

    class SpyTransport:
        def __init__(self) -> None:
            self.exists_paths: list[str] = []

        def exists(self, relative_path: str) -> bool:
            self.exists_paths.append(relative_path)
            return False

    findings: list = []
    transport = SpyTransport()
    _check_required_paths(transport, findings)
    expected_paths = list(required_paths_for_organization("generic"))

    assert [finding.path for finding in findings] == expected_paths
    assert transport.exists_paths == expected_paths
    assert all(finding.check == "required-path" for finding in findings)
    assert all(finding.severity == "blocker" for finding in findings)


def test_supported_organization_modes_only_contains_generic() -> None:
    from llm_wiki_core.vault.scaffold import supported_organization_modes

    assert supported_organization_modes() == ("generic",)


def test_generic_page_type_routes_immutable() -> None:
    from llm_wiki_core.vault.scaffold import get_organization_definition

    definition = get_organization_definition("generic")

    with pytest.raises(TypeError):
        definition.page_type_routes["concept"] = "other"

    assert (
        get_organization_definition("generic").page_type_routes["concept"]
        == "wiki/concepts"
    )


def test_unsupported_organization_mode_lists_supported_modes() -> None:
    from llm_wiki_core.vault.scaffold import (
        UnsupportedOrganizationMode,
        get_organization_definition,
    )

    with pytest.raises(UnsupportedOrganizationMode) as error:
        get_organization_definition("para")

    assert "Unsupported organization mode: para" in str(error.value)
    assert "generic" in str(error.value)
