from __future__ import annotations

import pytest


def test_route_for_page_type_reads_generic_definition() -> None:
    from llm_wiki_core.vault.routes import route_for_page_type

    assert route_for_page_type("source") == "wiki/sources"
    assert route_for_page_type("concept") == "wiki/concepts"
    assert route_for_page_type("question") == "wiki/questions"
    assert route_for_page_type("overview") == "wiki/overview.md"


def test_page_path_for_title_builds_collection_page_path() -> None:
    from llm_wiki_core.vault.routes import page_path_for_title

    assert page_path_for_title("source", "Example Source") == "wiki/sources/Example Source.md"
    assert page_path_for_title("question", "Artifact Parity") == "wiki/questions/Artifact Parity.md"


def test_collection_route_rejects_file_routes() -> None:
    from llm_wiki_core.vault.routes import collection_route_for_page_type

    with pytest.raises(ValueError, match="Page type overview routes to a file"):
        collection_route_for_page_type("overview")


def test_unknown_page_type_error_lists_supported_page_types() -> None:
    from llm_wiki_core.vault.routes import UnsupportedPageType, route_for_page_type

    with pytest.raises(UnsupportedPageType) as error:
        route_for_page_type("timeline")

    message = str(error.value)
    assert "Unsupported page type: timeline" in message
    assert "source" in message
    assert "question" in message


def test_search_roots_for_generic_preserves_current_search_order() -> None:
    from llm_wiki_core.vault.routes import search_roots_for_organization

    assert search_roots_for_organization("generic") == (
        "wiki/sources",
        "wiki/concepts",
        "wiki/entities",
        "wiki/questions",
        "wiki/comparisons",
    )


def test_route_helper_rejects_invalid_relative_routes(monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    invalid = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "source": "../outside"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": invalid)

    with pytest.raises(ValueError, match="Invalid route for page type source"):
        routes_module.route_for_page_type("source")


def test_route_helper_rejects_backslash_routes(monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    invalid = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "source": "wiki\\sources"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": invalid)

    with pytest.raises(ValueError, match="Invalid route for page type source"):
        routes_module.route_for_page_type("source")


def test_route_helper_rejects_empty_routes(monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    invalid = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "source": ""}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": invalid)

    with pytest.raises(ValueError, match="Invalid route for page type source"):
        routes_module.route_for_page_type("source")


def test_route_helper_rejects_dot_routes(monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    invalid = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "source": "."}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": invalid)

    with pytest.raises(ValueError, match="Invalid route for page type source"):
        routes_module.route_for_page_type("source")
