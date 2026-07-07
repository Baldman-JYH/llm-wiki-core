from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from llm_wiki_core.schema.frontmatter import build_frontmatter


BodyFactory = Callable[[str, str, str], str]


class UnsupportedOrganizationMode(ValueError):
    pass


@dataclass(frozen=True)
class SeedPage:
    relative_path: str
    page_type: str
    title: str
    body_factory: BodyFactory
    status: str = "seed"

    def render(self, created: str, updated: str, purpose: str) -> str:
        return build_frontmatter(
            page_type=self.page_type,
            title=self.title,
            created=created,
            updated=updated,
            status=self.status,
        ) + self.body_factory(purpose, created, updated)


@dataclass(frozen=True)
class OrganizationDefinition:
    name: str
    description: str
    required_directories: tuple[str, ...]
    seed_pages: tuple[SeedPage, ...]
    page_type_routes: Mapping[str, str]
    lint_required_paths: tuple[str, ...]
    search_page_types: tuple[str, ...] = ()
    lint_exemptions: tuple[str, ...] = ()
    adapter_notes: tuple[str, ...] = ()


def supported_organization_modes() -> tuple[str, ...]:
    return tuple(_ORGANIZATIONS)


def get_organization_definition(name: str = "generic") -> OrganizationDefinition:
    try:
        return _ORGANIZATIONS[name]
    except KeyError as error:
        supported = ", ".join(supported_organization_modes())
        raise UnsupportedOrganizationMode(
            f"Unsupported organization mode: {name}. Supported modes: {supported}."
        ) from error


def required_paths_for_organization(name: str = "generic") -> tuple[str, ...]:
    return get_organization_definition(name).lint_required_paths


def _index_body(_purpose: str, _date: str, _timestamp: str) -> str:
    return (
        "# Wiki Index\n\n"
        "## Concepts\n\n"
        "## Entities\n\n"
        "## Sources\n\n"
        "## Questions\n"
    )


def _log_body(_purpose: str, date: str, _timestamp: str) -> str:
    return (
        "# Operation Log\n\n"
        f"## [{date}] init | Vault scaffold\n"
        "- Summary: Created initial LLM Wiki scaffold.\n"
        "- Pages created: [[Wiki Index]], [[Hot Cache]], [[Overview]]\n"
    )


def _hot_body(_purpose: str, date: str, _timestamp: str) -> str:
    return (
        "# Recent Context\n\n"
        "## Last Updated\n"
        f"{date} - Vault initialized.\n\n"
        "## Key Recent Facts\n"
        "- The LLM Wiki scaffold exists.\n\n"
        "## Recent Changes\n"
        "- Created: [[Wiki Index]], [[Operation Log]], [[Overview]]\n\n"
        "## Active Threads\n"
        "- Add raw sources under `.raw/` and ingest them.\n"
    )


def _overview_body(purpose: str, _date: str, _timestamp: str) -> str:
    return (
        "# Overview\n\n"
        f"Purpose: {purpose}\n\n"
        "This vault follows the LLM Wiki pattern: raw sources stay in `.raw/`, "
        "the maintained wiki lives in `wiki/`, and agent behavior follows the project schema.\n"
    )


def _sub_index_body(title: str) -> BodyFactory:
    def body(_purpose: str, _date: str, _timestamp: str) -> str:
        return f"# {title}\n"

    return body


GENERIC_ORGANIZATION = OrganizationDefinition(
    name="generic",
    description="Default methodology-neutral LLM Wiki organization.",
    required_directories=(
        ".raw",
        "wiki",
        "wiki/sources",
        "wiki/entities",
        "wiki/concepts",
        "wiki/questions",
        "wiki/comparisons",
        "wiki/meta",
    ),
    seed_pages=(
        SeedPage("wiki/index.md", "meta", "Wiki Index", _index_body),
        SeedPage("wiki/log.md", "meta", "Operation Log", _log_body),
        SeedPage("wiki/hot.md", "meta", "Hot Cache", _hot_body),
        SeedPage("wiki/overview.md", "overview", "Overview", _overview_body),
        SeedPage("wiki/entities/_index.md", "meta", "Entities Index", _sub_index_body("Entities Index")),
        SeedPage("wiki/concepts/_index.md", "meta", "Concepts Index", _sub_index_body("Concepts Index")),
    ),
    page_type_routes=MappingProxyType({
        "source": "wiki/sources",
        "entity": "wiki/entities",
        "concept": "wiki/concepts",
        "question": "wiki/questions",
        "comparison": "wiki/comparisons",
        "meta": "wiki/meta",
        "overview": "wiki/overview.md",
    }),
    lint_required_paths=(
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
    ),
    search_page_types=(
        "source",
        "concept",
        "entity",
        "question",
        "comparison",
    ),
    adapter_notes=(
        "generic is the default organization mode",
        "methodology modes are optional future extensions",
    ),
)


_ORGANIZATIONS: dict[str, OrganizationDefinition] = {
    GENERIC_ORGANIZATION.name: GENERIC_ORGANIZATION,
}
