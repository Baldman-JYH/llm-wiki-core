from __future__ import annotations

from pathlib import PurePosixPath

from llm_wiki_core.vault.scaffold import get_organization_definition


class UnsupportedPageType(ValueError):
    pass


def route_for_page_type(page_type: str, organization: str = "generic") -> str:
    definition = get_organization_definition(organization)
    try:
        route = definition.page_type_routes[page_type]
    except KeyError as error:
        supported = ", ".join(definition.page_type_routes)
        raise UnsupportedPageType(
            f"Unsupported page type: {page_type}. Supported page types: {supported}."
        ) from error

    return _validated_route(page_type, route)


def collection_route_for_page_type(page_type: str, organization: str = "generic") -> str:
    route = route_for_page_type(page_type, organization=organization)
    if PurePosixPath(route).suffix.lower() == ".md":
        raise ValueError(f"Page type {page_type} routes to a file, not a collection: {route}")
    return route


def page_path_for_title(page_type: str, title: str, organization: str = "generic") -> str:
    route = collection_route_for_page_type(page_type, organization=organization)
    return (PurePosixPath(route) / f"{title}.md").as_posix()


def search_roots_for_organization(organization: str = "generic") -> tuple[str, ...]:
    definition = get_organization_definition(organization)
    return tuple(
        collection_route_for_page_type(page_type, organization=organization)
        for page_type in definition.search_page_types
    )


def _validated_route(page_type: str, route: str) -> str:
    path = PurePosixPath(route)
    if path.is_absolute() or ".." in path.parts or "\\" in route:
        raise ValueError(f"Invalid route for page type {page_type}: {route}")
    return path.as_posix()
