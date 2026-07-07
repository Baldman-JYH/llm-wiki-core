# R5.1 Organization Route Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make organization route definitions the source of truth for ingest, batch ingest, save, search, and status while preserving the released `generic` artifact behavior.

**Architecture:** Add a small route helper layer under `llm_wiki_core/vault/` and extend `OrganizationDefinition` with stable searchable page types. Operations continue to default to `generic`, but they stop duplicating route tables.

**Tech Stack:** Python standard library only, pytest, dependency-free package code.

## Global Constraints

- Only `generic` organization mode is supported in R5.1.
- Do not add vault-level persisted organization metadata.
- Do not add runtime LYT, PARA, Zettelkasten, DragonScale, comparison workflow, vector, hybrid, reranking, or LLM synthesis features.
- Preserve existing generic paths and CLI/result output shapes.
- Preserve artifact-level parity; do not claim byte-for-byte LLM prose parity.
- Do not add package dependencies; `pyproject.toml` dependencies must remain `[]`.
- Keep adapter-specific behavior outside neutral core unless it is a shared LLM Wiki rule.
- Commit messages must be written in Chinese.

---

## File Structure

- Modify `llm_wiki_core/vault/scaffold.py`
  - Add `search_page_types` to `OrganizationDefinition`.
  - Populate the `generic` search page-type order.
- Create `llm_wiki_core/vault/routes.py`
  - Central route lookup, route validation, collection-route enforcement, page path construction, and search-root resolution.
- Modify `llm_wiki_core/operations/ingest.py`
  - Use `page_path_for_title("source", title)` for generated source pages.
- Modify `llm_wiki_core/operations/ingest_batch.py`
  - Use the same source page path helper for conflict prediction.
- Modify `llm_wiki_core/operations/save.py`
  - Keep the current `question` / `concept` allowlist, then route through `page_path_for_title`.
- Modify `llm_wiki_core/operations/search.py`
  - Resolve searchable roots through organization routes at call time.
- Modify `llm_wiki_core/operations/status.py`
  - Resolve required paths through `required_paths_for_organization("generic")`.
- Create `tests/unit/test_organization_routes.py`
  - Route helper unit tests.
- Modify `tests/unit/test_organization_foundation.py`
  - Add generic search page-type assertion.
- Modify `tests/unit/test_ingest_operation.py`
  - Add route contract adoption test for ingest.
- Modify `tests/unit/test_batch_ingest_operation.py`
  - Add route contract adoption test for batch conflict prediction.
- Modify `tests/unit/test_query_save_operations.py`
  - Add route contract adoption tests for save.
- Modify `tests/unit/test_search_operation.py`
  - Add route contract adoption test for search roots.
- Modify `tests/unit/test_status_continue_operations.py`
  - Add route contract adoption test for status required paths.
- Create `tests/unit/test_r5_1_organization_route_adoption_docs.py`
  - Public documentation guard tests.
- Modify `docs/knowledge-organization.md`, `docs/roadmap.md`, `docs/roadmap-schedule.md`, and `docs/capability-mapping.md`
  - Document R5.1 as route adoption only.

---

### Task 1: Organization Route Helper Foundation

**Files:**
- Modify: `llm_wiki_core/vault/scaffold.py`
- Create: `llm_wiki_core/vault/routes.py`
- Create: `tests/unit/test_organization_routes.py`
- Modify: `tests/unit/test_organization_foundation.py`

**Interfaces:**
- Produces: `route_for_page_type(page_type: str, organization: str = "generic") -> str`
- Produces: `collection_route_for_page_type(page_type: str, organization: str = "generic") -> str`
- Produces: `page_path_for_title(page_type: str, title: str, organization: str = "generic") -> str`
- Produces: `search_roots_for_organization(organization: str = "generic") -> tuple[str, ...]`
- Produces: `UnsupportedPageType(ValueError)`
- Consumes: `llm_wiki_core.vault.scaffold.get_organization_definition`

- [ ] **Step 1: Write failing route helper tests**

Add this new file:

```python
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
```

Modify `tests/unit/test_organization_foundation.py` inside `test_generic_organization_definition_matches_mvp_structure`:

```python
    assert definition.search_page_types == (
        "source",
        "concept",
        "entity",
        "question",
        "comparison",
    )
```

- [ ] **Step 2: Run failing tests**

Run:

```powershell
python -m pytest tests/unit/test_organization_routes.py tests/unit/test_organization_foundation.py -q
```

Expected: FAIL because `llm_wiki_core.vault.routes` and `search_page_types` do not exist yet.

- [ ] **Step 3: Extend organization definition**

In `llm_wiki_core/vault/scaffold.py`, update the dataclass:

```python
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
```

In `GENERIC_ORGANIZATION`, add this argument after `lint_required_paths`:

```python
    search_page_types=(
        "source",
        "concept",
        "entity",
        "question",
        "comparison",
    ),
```

- [ ] **Step 4: Add route helper implementation**

Create `llm_wiki_core/vault/routes.py`:

```python
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
    if path.is_absolute() or ".." in path.parts or not route or "\\" in route:
        raise ValueError(f"Invalid route for page type {page_type}: {route}")
    return path.as_posix()
```

- [ ] **Step 5: Run focused tests**

Run:

```powershell
python -m pytest tests/unit/test_organization_routes.py tests/unit/test_organization_foundation.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add llm_wiki_core/vault/scaffold.py llm_wiki_core/vault/routes.py tests/unit/test_organization_routes.py tests/unit/test_organization_foundation.py
git commit -m "实现 R5.1 组织路由基础"
```

---

### Task 2: Ingest And Batch Ingest Route Adoption

**Files:**
- Modify: `llm_wiki_core/operations/ingest.py`
- Modify: `llm_wiki_core/operations/ingest_batch.py`
- Modify: `tests/unit/test_ingest_operation.py`
- Modify: `tests/unit/test_batch_ingest_operation.py`

**Interfaces:**
- Consumes: `page_path_for_title("source", title) -> str`
- Produces: source page writes and batch conflict messages that use organization source routes.

- [ ] **Step 1: Add failing ingest route adoption test**

Append to `tests/unit/test_ingest_operation.py`:

```python
def test_ingest_source_page_path_comes_from_organization_route(tmp_path, monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    routed = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "source": "wiki/routed-sources"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": routed)

    class SpyTransport:
        def __init__(self) -> None:
            self.write_calls: list[tuple[str, str]] = []
            self.files = {
                ".raw/articles/example.md": "Example source body.",
                ".raw/.manifest.json": '{"schema_version": 1, "updated": "", "sources": {}}\n',
                "wiki/index.md": "# Wiki Index\n\n## Sources\n",
                "wiki/log.md": "# Operation Log\n\n",
                "wiki/hot.md": "# Recent Context\n",
            }

        def exists(self, relative_path: str) -> bool:
            return relative_path in self.files

        def read_text(self, relative_path: str) -> str:
            return self.files[relative_path]

        def write_text(self, relative_path: str, content: str) -> str:
            self.write_calls.append((relative_path, content))
            self.files[relative_path] = content
            return relative_path

    transport = SpyTransport()

    result = ingest_source(tmp_path, ".raw/articles/example.md", transport=transport)

    written_paths = [path for path, _content in transport.write_calls]
    assert result.files_created == ["wiki/routed-sources/Example.md"]
    assert "wiki/routed-sources/Example.md" in written_paths
    manifest = json.loads(transport.files[".raw/.manifest.json"])
    assert manifest["sources"]["articles/example.md"]["generated_pages"] == [
        "wiki/routed-sources/Example.md"
    ]
```

- [ ] **Step 2: Add failing batch route adoption test**

Append to `tests/unit/test_batch_ingest_operation.py`:

```python
def test_ingest_batch_conflict_prediction_uses_organization_source_route(tmp_path, monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.operations.ingest_batch import ingest_batch
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    routed = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "source": "wiki/routed-sources"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": routed)

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "a/report.md", "# First Report\n\nAlpha source.")
    _write_raw(tmp_path, "b/report.md", "# Second Report\n\nBeta source.")

    result = ingest_batch(tmp_path, ".raw")

    assert result.status == "partial"
    assert result.succeeded == 1
    assert result.failed == 1
    assert "wiki/routed-sources/Report.md" in (result.items[1].error_message or "")
    assert (tmp_path / "wiki" / "routed-sources" / "Report.md").is_file()
```

- [ ] **Step 3: Run failing tests**

Run:

```powershell
python -m pytest tests/unit/test_ingest_operation.py::test_ingest_source_page_path_comes_from_organization_route tests/unit/test_batch_ingest_operation.py::test_ingest_batch_conflict_prediction_uses_organization_source_route -q
```

Expected: FAIL because operations still build `wiki/sources` paths locally.

- [ ] **Step 4: Update ingest**

In `llm_wiki_core/operations/ingest.py`, add:

```python
from llm_wiki_core.vault.routes import page_path_for_title
```

Replace:

```python
    source_page_relative = Path("wiki") / "sources" / f"{title}.md"
    source_page_path = source_page_relative.as_posix()
```

with:

```python
    source_page_path = page_path_for_title("source", title)
```

- [ ] **Step 5: Update batch ingest**

In `llm_wiki_core/operations/ingest_batch.py`, add:

```python
from llm_wiki_core.vault.routes import page_path_for_title
```

Replace `_target_source_page` with:

```python
def _target_source_page(source_path: str) -> str:
    title = _title_from_source_path(_normalize_source_path(source_path))
    return page_path_for_title("source", title)
```

- [ ] **Step 6: Run focused tests**

Run:

```powershell
python -m pytest tests/unit/test_ingest_operation.py tests/unit/test_batch_ingest_operation.py tests/unit/test_organization_routes.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add llm_wiki_core/operations/ingest.py llm_wiki_core/operations/ingest_batch.py tests/unit/test_ingest_operation.py tests/unit/test_batch_ingest_operation.py
git commit -m "接入 R5.1 ingest 组织路由"
```

---

### Task 3: Save Route Adoption

**Files:**
- Modify: `llm_wiki_core/operations/save.py`
- Modify: `tests/unit/test_query_save_operations.py`

**Interfaces:**
- Consumes: `page_path_for_title(target_type, page_title) -> str`
- Preserves: `target_type` values are still limited to `question` and `concept`.

- [ ] **Step 1: Add failing save route adoption tests**

Append to `tests/unit/test_query_save_operations.py`:

```python
def test_save_question_page_path_comes_from_organization_route(tmp_path, monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    routed = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "question": "wiki/routed-questions"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": routed)

    init_vault(tmp_path, purpose="Route save question")

    result = save_insight(
        tmp_path,
        content="Route-backed question save.",
        title="Route Question",
    )

    assert result.page_path == "wiki/routed-questions/Route Question.md"
    assert (tmp_path / "wiki" / "routed-questions" / "Route Question.md").is_file()
    assert not (tmp_path / "wiki" / "questions" / "Route Question.md").exists()


def test_save_concept_page_path_comes_from_organization_route(tmp_path, monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    routed = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "concept": "wiki/routed-concepts"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": routed)

    init_vault(tmp_path, purpose="Route save concept")

    result = save_insight(
        tmp_path,
        content="Route-backed concept save.",
        title="Route Concept",
        target_type="concept",
    )

    assert result.page_path == "wiki/routed-concepts/Route Concept.md"
    assert (tmp_path / "wiki" / "routed-concepts" / "Route Concept.md").is_file()
    assert not (tmp_path / "wiki" / "concepts" / "Route Concept.md").exists()


def test_save_target_type_allowlist_is_preserved(tmp_path) -> None:
    import pytest

    from llm_wiki_core.operations.save import save_insight

    with pytest.raises(ValueError, match="target_type must be question or concept"):
        save_insight(tmp_path, content="Entity saves are not part of R5.1.", target_type="entity")
```

- [ ] **Step 2: Run failing tests**

Run:

```powershell
python -m pytest tests/unit/test_query_save_operations.py::test_save_question_page_path_comes_from_organization_route tests/unit/test_query_save_operations.py::test_save_concept_page_path_comes_from_organization_route tests/unit/test_query_save_operations.py::test_save_target_type_allowlist_is_preserved -q
```

Expected: first two tests FAIL because save still uses local folder mapping; allowlist test may already PASS.

- [ ] **Step 3: Update save implementation**

In `llm_wiki_core/operations/save.py`, add:

```python
from llm_wiki_core.vault.routes import page_path_for_title
```

Replace:

```python
    folder = _folder_for_type(target_type)
    page_relative = Path("wiki") / folder / f"{page_title}.md"
    page_path = page_relative.as_posix()
```

with:

```python
    page_path = _page_path_for_type(target_type, page_title)
```

Replace `_folder_for_type` with:

```python
def _page_path_for_type(target_type: str, page_title: str) -> str:
    if target_type not in {"question", "concept"}:
        raise ValueError("target_type must be question or concept")
    return page_path_for_title(target_type, page_title)
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests/unit/test_query_save_operations.py tests/unit/test_organization_routes.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add llm_wiki_core/operations/save.py tests/unit/test_query_save_operations.py
git commit -m "接入 R5.1 save 组织路由"
```

---

### Task 4: Search And Status Route Adoption

**Files:**
- Modify: `llm_wiki_core/operations/search.py`
- Modify: `llm_wiki_core/operations/status.py`
- Modify: `tests/unit/test_search_operation.py`
- Modify: `tests/unit/test_status_continue_operations.py`

**Interfaces:**
- Consumes: `search_roots_for_organization("generic") -> tuple[str, ...]`
- Consumes: `required_paths_for_organization("generic") -> tuple[str, ...]`
- Preserves: `SearchWikiResult.searched_roots` order for `generic`.

- [ ] **Step 1: Add failing search route adoption test**

Append to `tests/unit/test_search_operation.py`:

```python
def test_search_wiki_roots_come_from_organization_routes(tmp_path, monkeypatch) -> None:
    import llm_wiki_core.operations.search as search_module
    from llm_wiki_core.operations.search import search_wiki

    monkeypatch.setattr(
        search_module,
        "search_roots_for_organization",
        lambda _organization="generic": ("wiki/routed-search",),
    )

    class RoutedSearchTransport:
        def __init__(self) -> None:
            self.list_roots: list[str] = []
            self.files = {
                "wiki/routed-search/Route Result.md": "# Route Result\n\nDurable routed search content.",
                "wiki/sources/Ignored.md": "# Ignored\n\nDurable content outside routed roots.",
            }

        def list_markdown(self, root: str = "wiki") -> list[str]:
            self.list_roots.append(root)
            return sorted(path for path in self.files if path.startswith(root + "/") and path.endswith(".md"))

        def read_text(self, relative_path: str) -> str:
            return self.files[relative_path]

    transport = RoutedSearchTransport()

    result = search_wiki(tmp_path, "durable routed", transport=transport)

    assert result.searched_roots == ["wiki/routed-search"]
    assert transport.list_roots == ["wiki/routed-search"]
    assert [page.path for page in result.results] == ["wiki/routed-search/Route Result.md"]
```

- [ ] **Step 2: Add failing status route adoption test**

Append to `tests/unit/test_status_continue_operations.py`:

```python
def test_status_required_paths_come_from_organization_contract(tmp_path, monkeypatch) -> None:
    import llm_wiki_core.operations.status as status_module
    from llm_wiki_core.operations.status import status_wiki

    monkeypatch.setattr(
        status_module,
        "required_paths_for_organization",
        lambda _organization="generic": ("wiki/routed-required.md",),
    )

    class SpyTransport:
        def __init__(self) -> None:
            self.exists_paths: list[str] = []

        def exists(self, relative_path: str) -> bool:
            self.exists_paths.append(relative_path)
            return False

    transport = SpyTransport()

    result = status_wiki(tmp_path, transport=transport)

    assert result.status == "incomplete"
    assert result.missing_required_paths == ["wiki/routed-required.md"]
    assert "wiki/routed-required.md" in transport.exists_paths
```

- [ ] **Step 3: Run failing tests**

Run:

```powershell
python -m pytest tests/unit/test_search_operation.py::test_search_wiki_roots_come_from_organization_routes tests/unit/test_status_continue_operations.py::test_status_required_paths_come_from_organization_contract -q
```

Expected: FAIL because search and status still use local route constants.

- [ ] **Step 4: Update search implementation**

In `llm_wiki_core/operations/search.py`, replace the `SEARCH_ROOTS` tuple with:

```python
from llm_wiki_core.vault.routes import search_roots_for_organization
```

Update `search_wiki`:

```python
    search_roots = search_roots_for_organization("generic")
    documents = _read_search_documents(active_transport, search_roots)
```

Update the result:

```python
        searched_roots=list(search_roots),
```

Replace `_read_search_documents` with:

```python
def _read_search_documents(transport: object, search_roots: tuple[str, ...]) -> list[SearchDocument]:
    documents: list[SearchDocument] = []
    for root in search_roots:
        for page in transport.list_markdown(root):  # type: ignore[attr-defined]
            documents.append(
                SearchDocument(
                    path=page,
                    title=Path(page).stem,
                    text=transport.read_text(page),  # type: ignore[attr-defined]
                )
            )
    return documents
```

- [ ] **Step 5: Update status implementation**

In `llm_wiki_core/operations/status.py`, remove the local `REQUIRED_PATHS` list and add:

```python
from llm_wiki_core.vault.scaffold import required_paths_for_organization
```

Replace:

```python
    missing = [path for path in REQUIRED_PATHS if not active_transport.exists(path)]  # type: ignore[attr-defined]
```

with:

```python
    required_paths = required_paths_for_organization("generic")
    missing = [path for path in required_paths if not active_transport.exists(path)]  # type: ignore[attr-defined]
```

- [ ] **Step 6: Run focused tests**

Run:

```powershell
python -m pytest tests/unit/test_search_operation.py tests/unit/test_status_continue_operations.py tests/unit/test_organization_routes.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add llm_wiki_core/operations/search.py llm_wiki_core/operations/status.py tests/unit/test_search_operation.py tests/unit/test_status_continue_operations.py
git commit -m "接入 R5.1 search status 组织契约"
```

---

### Task 5: Documentation, Guard Tests, And Final Verification

**Files:**
- Create: `tests/unit/test_r5_1_organization_route_adoption_docs.py`
- Modify: `docs/knowledge-organization.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/roadmap-schedule.md`
- Modify: `docs/capability-mapping.md`

**Interfaces:**
- Consumes: R5.1 implementation behavior from Tasks 1-4.
- Produces: public docs that accurately describe R5.1 as route adoption only.

- [ ] **Step 1: Add failing docs guard tests**

Create `tests/unit/test_r5_1_organization_route_adoption_docs.py`:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_knowledge_organization_doc_tracks_r5_1_route_adoption() -> None:
    text = _read("docs/knowledge-organization.md")

    assert "R5.1 adds organization route adoption" in text
    assert "ingest, batch ingest, save, search, and status read routes from the organization contract" in text
    assert "R5.1 does not add non-generic organization modes" in text


def test_capability_mapping_tracks_route_adoption_without_methodology_claims() -> None:
    text = _read("docs/capability-mapping.md")

    assert "| Organization route adoption | Core | R5.1 complete |" in text
    assert "| Methodology modes | Deferred extension | Deferred |" in text
    assert "| DragonScale or log-folding memory | Deferred extension | Deferred |" in text


def test_roadmap_documents_r5_1_route_adoption_and_future_modes() -> None:
    roadmap = _read("docs/roadmap.md")
    schedule = _read("docs/roadmap-schedule.md")

    assert "R5.1 organization route adoption is complete" in roadmap
    assert "generic remains the default organization mode" in roadmap
    assert "### R5.1: Organization Route Adoption Foundation" in schedule
    assert "Status: complete." in schedule
    assert "Non-generic organization modes remain future R5.x work." in schedule


def test_r5_1_docs_do_not_claim_advanced_modes_are_complete() -> None:
    combined = "\n".join(
        [
            _read("docs/knowledge-organization.md"),
            _read("docs/roadmap.md"),
            _read("docs/roadmap-schedule.md"),
            _read("docs/capability-mapping.md"),
        ]
    )

    forbidden = [
        "LYT is complete",
        "PARA is complete",
        "Zettelkasten is complete",
        "DragonScale is complete",
        "semantic stale-claim lint is complete",
        "non-generic organization modes are complete",
    ]
    for phrase in forbidden:
        assert phrase not in combined
```

- [ ] **Step 2: Run failing docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r5_1_organization_route_adoption_docs.py -q
```

Expected: FAIL because public docs do not mention R5.1 yet.

- [ ] **Step 3: Update `docs/knowledge-organization.md`**

Add a new section after the R5.0 boundary:

```markdown
## R5.1 Route Adoption

R5.1 adds organization route adoption.

The `generic` organization definition remains the only supported runtime mode, but core operations now consume the organization contract more consistently. Ingest, batch ingest, save, search, and status read routes from the organization contract instead of maintaining separate local route tables.

R5.1 does not add non-generic organization modes. LYT, PARA, Zettelkasten, DragonScale, comparison workflow runtime, semantic stale-claim lint, vector or hybrid retrieval, and advanced Claude adapter behavior remain future work.
```

- [ ] **Step 4: Update `docs/roadmap.md`**

In the Knowledge Organization Roadmap section, replace the R5.0 status paragraph with:

```markdown
R5.0 knowledge organization foundation is complete. R5.1 organization route adoption is complete. generic remains the default organization mode.
```

Keep the existing future R5.x bullet list intact.

- [ ] **Step 5: Update `docs/roadmap-schedule.md`**

Add this section after R5.0:

```markdown
### R5.1: Organization Route Adoption Foundation

Window: 2026-07-07

Status: complete.

Scope:

- Organization route helper layer.
- `generic` searchable page-type order.
- Ingest and batch ingest source page route adoption.
- Save question and concept route adoption.
- Search roots sourced from organization routes.
- Status required paths sourced from the organization contract.
- Public documentation and guard tests for route-adoption-only support.

Completed outcome:

- `generic` artifact paths remain compatible.
- Ingest, batch ingest, save, search, and status no longer maintain independent generic route tables.
- Search root order remains stable for current users.
- Non-generic organization modes remain future R5.x work.

Non-scope:

- Non-generic organization modes.
- Vault-level persisted organization metadata.
- LYT, PARA, Zettelkasten, DragonScale, comparison workflow runtime, semantic stale-claim lint, vector or hybrid retrieval, and advanced adapter behavior remain future work.
```

- [ ] **Step 6: Update `docs/capability-mapping.md`**

Add this row near the knowledge organization rows:

```markdown
| Organization route adoption | Core | R5.1 complete | Use the same generic route contract for local Codex workflows | Use the same generic route contract for local Claude workflows | Foundation only; no non-generic modes |
```

- [ ] **Step 7: Run focused docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r5_1_organization_route_adoption_docs.py tests/unit/test_r5_0_knowledge_organization_docs.py -q
```

Expected: PASS.

- [ ] **Step 8: Run final verification**

Run:

```powershell
python -m pytest tests/unit/test_organization_routes.py tests/unit/test_organization_foundation.py tests/unit/test_ingest_operation.py tests/unit/test_batch_ingest_operation.py tests/unit/test_query_save_operations.py tests/unit/test_search_operation.py tests/unit/test_status_continue_operations.py tests/unit/test_r5_1_organization_route_adoption_docs.py -q
```

Expected: PASS.

Run:

```powershell
python -m pytest -q
```

Expected: PASS with the same skip profile as the R5.1 baseline unless new docs tests increase the pass count.

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

Run:

```powershell
rg -n "dependencies = \\[\\]" pyproject.toml
```

Expected: `dependencies = []`.

Run:

```powershell
git ls-files .superpowers codex_doc
```

Expected: no tracked files from `.superpowers` or external `codex_doc`.

- [ ] **Step 9: Commit**

Run:

```powershell
git add docs/knowledge-organization.md docs/roadmap.md docs/roadmap-schedule.md docs/capability-mapping.md tests/unit/test_r5_1_organization_route_adoption_docs.py
git commit -m "补充 R5.1 组织路由文档与验证"
```

---

## Whole-Branch Verification

After Task 5 completes, run:

```powershell
git status -sb
git log --oneline --decorate main..HEAD
python -m pytest -q
git diff --check
rg -n "dependencies = \\[\\]" pyproject.toml
git ls-files .superpowers codex_doc
```

Expected:

- branch contains the R5.1 design commit, implementation commits, and docs commit;
- full pytest suite passes;
- whitespace check passes;
- dependency boundary remains empty;
- no `.superpowers` or `codex_doc` files are tracked.

If verification passes, proceed to whole-branch review before merging to `main`.
