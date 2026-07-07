# R5.0 Knowledge Organization Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a neutral organization foundation while preserving the existing `generic` LLM Wiki behavior.

**Architecture:** Extract the current generic scaffold into a small organization-definition layer under `llm_wiki_core/vault/scaffold.py`, move frontmatter creation into `llm_wiki_core/schema/frontmatter.py`, and make `init`, CLI, and lint consume that shared contract. Only `generic` ships in R5.0; methodology modes remain documented future extensions.

**Tech Stack:** Python standard library only, pytest, Markdown docs, no runtime dependencies.

## Global Constraints

- `generic` remains the default organization mode.
- Existing `llm-wiki init <vault> --purpose "..."` behavior must stay compatible.
- R5.0 must not implement LYT, PARA, Zettelkasten, DragonScale, semantic stale-claim lint, vector or hybrid retrieval, Claude hooks, Claude subagents, or `.claude-plugin` packaging.
- Raw sources remain immutable under `.raw/`.
- Wiki artifacts remain durable Markdown files.
- Artifact-level equivalence matters more than byte-for-byte prose matching.
- Windows native PowerShell and macOS/POSIX local use must remain supported.
- Do not add third-party runtime dependencies.
- Commit messages must be written in Chinese.

---

## File Structure

- Create `tests/unit/test_organization_foundation.py`: unit tests for frontmatter and organization definitions.
- Modify `llm_wiki_core/schema/frontmatter.py`: frontmatter builder used by seed pages.
- Modify `llm_wiki_core/vault/scaffold.py`: organization dataclasses, generic definition, supported mode lookup, and required path helpers.
- Modify `llm_wiki_core/operations/init.py`: use organization definitions while preserving current generic output.
- Modify `llm_wiki_core/cli.py`: add explicit `--organization generic` option for `init`.
- Modify `tests/unit/test_init_operation.py`: init and CLI organization behavior tests.
- Modify `llm_wiki_core/operations/lint.py`: read required paths from the organization definition.
- Modify `tests/unit/test_lint_operation.py`: regression test proving lint uses the shared organization contract.
- Create `docs/knowledge-organization.md`: public R5.0 boundary document.
- Modify `docs/capability-mapping.md`: add R5.0 foundation status and keep methodology modes deferred.
- Modify `docs/roadmap.md`: describe foundation-first knowledge organization path.
- Modify `docs/roadmap-schedule.md`: add R5.0 milestone.
- Create `tests/unit/test_r5_0_knowledge_organization_docs.py`: documentation guard tests.

---

### Task 1: Organization Definition And Frontmatter Foundation

**Files:**
- Create: `tests/unit/test_organization_foundation.py`
- Modify: `llm_wiki_core/schema/frontmatter.py`
- Modify: `llm_wiki_core/vault/scaffold.py`

**Interfaces:**
- Produces: `build_frontmatter(page_type: str, title: str, created: str, updated: str, status: str = "seed") -> str`
- Produces: `SeedPage(relative_path: str, page_type: str, title: str, body_factory: BodyFactory, status: str = "seed")`
- Produces: `OrganizationDefinition`
- Produces: `UnsupportedOrganizationMode(ValueError)`
- Produces: `get_organization_definition(name: str = "generic") -> OrganizationDefinition`
- Produces: `supported_organization_modes() -> tuple[str, ...]`
- Produces: `required_paths_for_organization(name: str = "generic") -> tuple[str, ...]`
- Consumes: no new project interfaces

- [ ] **Step 1: Write failing organization foundation tests**

Add this file:

```python
from __future__ import annotations

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

    seed_paths = {page.relative_path for page in definition.seed_pages}
    assert {
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md",
        "wiki/overview.md",
        "wiki/entities/_index.md",
        "wiki/concepts/_index.md",
    }.issubset(seed_paths)


def test_generic_seed_pages_render_existing_mvp_content() -> None:
    from llm_wiki_core.vault.scaffold import get_organization_definition

    definition = get_organization_definition()
    rendered = {
        page.relative_path: page.render(
            created="2026-07-07",
            updated="2026-07-07T08:09:10+08:00",
            purpose="Map an example codebase",
        )
        for page in definition.seed_pages
    }

    assert rendered["wiki/index.md"].startswith("---\ntype: meta\n")
    assert "# Wiki Index" in rendered["wiki/index.md"]
    assert "## Concepts" in rendered["wiki/index.md"]
    assert "## Entities" in rendered["wiki/index.md"]
    assert "## Sources" in rendered["wiki/index.md"]
    assert "## Questions" in rendered["wiki/index.md"]
    assert "Created initial LLM Wiki scaffold." in rendered["wiki/log.md"]
    assert "Vault initialized." in rendered["wiki/hot.md"]
    assert "Map an example codebase" in rendered["wiki/overview.md"]


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


def test_unsupported_organization_mode_lists_supported_modes() -> None:
    from llm_wiki_core.vault.scaffold import (
        UnsupportedOrganizationMode,
        get_organization_definition,
    )

    with pytest.raises(UnsupportedOrganizationMode) as error:
        get_organization_definition("para")

    assert "Unsupported organization mode: para" in str(error.value)
    assert "generic" in str(error.value)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_organization_foundation.py -q
```

Expected: FAIL because `build_frontmatter`, organization dataclasses, and lookup helpers are not implemented.

- [ ] **Step 3: Implement frontmatter helper**

Replace `llm_wiki_core/schema/frontmatter.py` with:

```python
from __future__ import annotations


def build_frontmatter(
    page_type: str,
    title: str,
    created: str,
    updated: str,
    status: str = "seed",
) -> str:
    return (
        "---\n"
        f"type: {page_type}\n"
        f'title: "{title}"\n'
        f"created: {created}\n"
        f"updated: {updated}\n"
        f"status: {status}\n"
        "---\n\n"
    )
```

- [ ] **Step 4: Implement generic organization definition**

Replace `llm_wiki_core/vault/scaffold.py` with:

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

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
    page_type_routes={
        "source": "wiki/sources",
        "entity": "wiki/entities",
        "concept": "wiki/concepts",
        "question": "wiki/questions",
        "comparison": "wiki/comparisons",
        "meta": "wiki/meta",
        "overview": "wiki/overview.md",
    },
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
    adapter_notes=(
        "generic is the default organization mode",
        "methodology modes are optional future extensions",
    ),
)


_ORGANIZATIONS: dict[str, OrganizationDefinition] = {
    GENERIC_ORGANIZATION.name: GENERIC_ORGANIZATION,
}
```

- [ ] **Step 5: Run task tests**

Run:

```powershell
python -m pytest tests/unit/test_organization_foundation.py -q
```

Expected: `5 passed`.

- [ ] **Step 6: Commit Task 1**

Run:

```powershell
git add tests/unit/test_organization_foundation.py llm_wiki_core/schema/frontmatter.py llm_wiki_core/vault/scaffold.py
git commit -m "添加 R5.0 组织定义基础"
```

---

### Task 2: Init And CLI Organization Option

**Files:**
- Modify: `llm_wiki_core/operations/init.py`
- Modify: `llm_wiki_core/cli.py`
- Modify: `tests/unit/test_init_operation.py`

**Interfaces:**
- Consumes: `get_organization_definition(name: str = "generic")`
- Produces: `init_vault(vault_root, purpose, adapter="codex", organization="generic")`
- Produces: `OperationResult.organization: str`
- Produces: CLI option `llm-wiki init <vault> --purpose "..." --organization generic`

- [ ] **Step 1: Add failing init and CLI tests**

Append these tests to `tests/unit/test_init_operation.py`:

```python

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
    import json

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
    import json

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_init_operation.py -q
```

Expected: FAIL because `organization` is not accepted and CLI lacks `--organization`.

- [ ] **Step 3: Refactor init to consume organization definitions**

Modify `llm_wiki_core/operations/init.py`:

1. Add import:

```python
from llm_wiki_core.vault.scaffold import get_organization_definition
```

2. Add `organization` to `OperationResult`:

```python
organization: str = "generic"
```

3. Change the function signature:

```python
def init_vault(
    vault_root: str | Path,
    purpose: str,
    adapter: str = "codex",
    organization: str = "generic",
) -> OperationResult:
```

4. Resolve the definition before creating the root directory:

```python
definition = get_organization_definition(organization)
root = Path(vault_root)
if root.exists() and not root.is_dir():
    raise NotADirectoryError(f"Vault root is not a directory: {root}")
```

5. Replace the required directory loop:

```python
for relative in definition.required_directories:
    (root / relative).mkdir(parents=True, exist_ok=True)
```

6. Replace `seed_pages` construction with:

```python
seed_pages = {
    root / page.relative_path: page.render(
        created=date,
        updated=timestamp,
        purpose=purpose,
    )
    for page in definition.seed_pages
}
```

7. Return `organization=definition.name` in `OperationResult`.

8. Remove private helper functions that moved into `vault/scaffold.py`: `_required_directories`, `_frontmatter`, `_index_page`, `_log_page`, `_hot_page`, `_overview_page`, and `_sub_index_page`.

- [ ] **Step 4: Add CLI option**

In `llm_wiki_core/cli.py`, add this to the `init_parser` setup:

```python
init_parser.add_argument(
    "--organization",
    default="generic",
    help="Organization mode to use. R5.0 supports generic.",
)
```

Change `_execute` init branch to:

```python
if args.command == "init":
    return init_vault(
        args.vault,
        purpose=args.purpose,
        adapter="codex",
        organization=args.organization,
    )
```

- [ ] **Step 5: Run task tests**

Run:

```powershell
python -m pytest tests/unit/test_init_operation.py tests/unit/test_organization_foundation.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit Task 2**

Run:

```powershell
git add llm_wiki_core/operations/init.py llm_wiki_core/cli.py tests/unit/test_init_operation.py
git commit -m "接入 R5.0 初始化组织模式"
```

---

### Task 3: Lint Uses Organization Required Paths

**Files:**
- Modify: `llm_wiki_core/operations/lint.py`
- Modify: `tests/unit/test_lint_operation.py`

**Interfaces:**
- Consumes: `required_paths_for_organization(name: str = "generic") -> tuple[str, ...]`
- Produces: no new public CLI behavior

- [ ] **Step 1: Add failing lint contract test**

Append this test to `tests/unit/test_lint_operation.py`:

```python

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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_lint_operation.py::test_lint_required_paths_come_from_organization_definition -q
```

Expected: FAIL because `lint.py` still owns a hard-coded required path list.

- [ ] **Step 3: Import required path helper**

Add this import to `llm_wiki_core/operations/lint.py`:

```python
from llm_wiki_core.vault.scaffold import required_paths_for_organization
```

- [ ] **Step 4: Replace hard-coded required paths**

Change `_check_required_paths` to:

```python
def _check_required_paths(transport: object, findings: list[LintFinding]) -> None:
    for relative in required_paths_for_organization("generic"):
        if not transport.exists(relative):  # type: ignore[attr-defined]
            findings.append(LintFinding("blocker", "required-path", relative, "Required path is missing."))
```

- [ ] **Step 5: Run lint tests**

Run:

```powershell
python -m pytest tests/unit/test_lint_operation.py tests/unit/test_organization_foundation.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit Task 3**

Run:

```powershell
git add llm_wiki_core/operations/lint.py tests/unit/test_lint_operation.py
git commit -m "让 lint 使用组织路径契约"
```

---

### Task 4: R5.0 Public Documentation And Guard Tests

**Files:**
- Create: `docs/knowledge-organization.md`
- Modify: `docs/capability-mapping.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/roadmap-schedule.md`
- Create: `tests/unit/test_r5_0_knowledge_organization_docs.py`

**Interfaces:**
- Consumes: R5.0 spec and ADR language
- Produces: public documentation guardrails for foundation-only support

- [ ] **Step 1: Add failing docs guard tests**

Create `tests/unit/test_r5_0_knowledge_organization_docs.py`:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_knowledge_organization_doc_defines_foundation_boundary() -> None:
    text = _read("docs/knowledge-organization.md")

    assert "generic is the default organization mode" in text
    assert "Organization modes are optional extensions" in text
    assert "R5.0 does not implement full LYT, PARA, or Zettelkasten runtime behavior" in text
    assert "Karpathy's LLM Wiki pattern remains canonical" in text
    assert "raw sources / wiki / schema" in text


def test_capability_mapping_tracks_r5_foundation_without_methodology_claims() -> None:
    text = _read("docs/capability-mapping.md")

    assert "| Knowledge organization foundation | Core | R5.0 complete |" in text
    assert "| Methodology modes | Deferred extension | Deferred |" in text
    assert "| DragonScale or log-folding memory | Deferred extension | Deferred |" in text


def test_roadmap_documents_r5_0_foundation_and_future_methodology_modes() -> None:
    roadmap = _read("docs/roadmap.md")
    schedule = _read("docs/roadmap-schedule.md")

    assert "R5.0 knowledge organization foundation is complete" in roadmap
    assert "generic remains the default organization mode" in roadmap
    assert "### R5.0: Knowledge Organization Foundation" in schedule
    assert "Status: complete." in schedule
    assert "Full LYT, PARA, Zettelkasten, DragonScale, and semantic stale-claim lint remain future R5.x work." in schedule


def test_r5_docs_do_not_claim_advanced_modes_are_complete() -> None:
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
    ]
    for phrase in forbidden:
        assert phrase not in combined
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r5_0_knowledge_organization_docs.py -q
```

Expected: FAIL because public docs are not added or updated yet.

- [ ] **Step 3: Create knowledge organization document**

Create `docs/knowledge-organization.md`:

```markdown
# Knowledge Organization

R5.0 adds the foundation for knowledge organization modes.

Karpathy's LLM Wiki pattern remains canonical: humans provide raw sources, the agent maintains durable Markdown wiki artifacts, and the wiki keeps schema, index, log, hot context, links, and lintable health. The core structure is still raw sources / wiki / schema.

## Default Mode

generic is the default organization mode.

It creates the same methodology-neutral scaffold used by the MVP:

- `.raw/.manifest.json`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`
- `wiki/overview.md`
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/questions/`
- `wiki/comparisons/`
- `wiki/meta/`

## Optional Extensions

Organization modes are optional extensions.

R5.0 does not implement full LYT, PARA, or Zettelkasten runtime behavior. It creates the neutral contract that future R5.x milestones can use to add those modes safely.

Future organization modes must preserve:

- raw source immutability;
- durable Markdown wiki artifacts;
- index, log, and hot context continuity;
- flat frontmatter minimums;
- artifact-level equivalence across adapters.

## R5.0 Boundary

R5.0 supports:

- explicit `generic` organization definition;
- scaffold and frontmatter helpers;
- init and lint integration with the organization contract;
- public documentation for future mode boundaries.

R5.0 does not support:

- full LYT, PARA, or Zettelkasten migration;
- DragonScale or log-folding memory;
- semantic stale-claim lint;
- vector or hybrid retrieval;
- Obsidian Dataview, Bases, canvas, or plugin-specific dashboards;
- Claude hooks, subagents, or `.claude-plugin` packaging.
```

- [ ] **Step 4: Update capability mapping**

Add this row before `DragonScale or log-folding memory` in `docs/capability-mapping.md`:

```markdown
| Knowledge organization foundation | Core | R5.0 complete | Expose `generic` as the default organization mode | Expose `generic` as the default organization mode | Foundation only; optional methodology modes remain deferred |
```

Keep the existing deferred Methodology modes and DragonScale rows unchanged.

- [ ] **Step 5: Update roadmap**

In `docs/roadmap.md`, replace the Knowledge Organization Roadmap section with:

```markdown
## Knowledge Organization Roadmap

R5.0 knowledge organization foundation is complete. `generic` remains the default organization mode.

Future R5.x work:

- Optional LYT / PARA / Zettelkasten templates.
- Comparison page workflows.
- DragonScale or log-folding memory extension.
- Advanced lint for semantic tiling and stale claims.
```

- [ ] **Step 6: Update roadmap schedule**

Add this subsection under `## R5: Knowledge Organization` in `docs/roadmap-schedule.md`:

```markdown
### R5.0: Knowledge Organization Foundation

Window: 2026-07-07

Status: complete.

Scope:

- Explicit `generic` organization definition.
- Shared scaffold and frontmatter helpers.
- `init` support for explicit `--organization generic`.
- Lint required paths sourced from the organization contract.
- Public documentation and guard tests for foundation-only support.

Completed outcome:

- `generic` remains the default organization mode.
- Organization modes are optional extensions.
- The core has a neutral extension point for future LYT, PARA, Zettelkasten, comparison workflows, DragonScale, and advanced lint.

Non-scope:

- Full LYT, PARA, Zettelkasten, DragonScale, and semantic stale-claim lint remain future R5.x work.
- No existing vault migration is provided in R5.0.
- No adapter claims advanced methodology support in R5.0.
```

- [ ] **Step 7: Run docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r5_0_knowledge_organization_docs.py tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_3_claude_adapter_assets.py -q
```

Expected: all tests pass, with existing POSIX skips on Windows.

- [ ] **Step 8: Commit Task 4**

Run:

```powershell
git add docs/knowledge-organization.md docs/capability-mapping.md docs/roadmap.md docs/roadmap-schedule.md tests/unit/test_r5_0_knowledge_organization_docs.py
git commit -m "补充 R5.0 知识组织文档边界"
```

---

### Task 5: Final Verification And Branch Review

**Files:**
- Modify only if verification finds a concrete defect in files changed by Tasks 1-4.

**Interfaces:**
- Consumes: all R5.0 changes
- Produces: verified R5.0 development branch ready for review, merge, release decision, or follow-up implementation

- [ ] **Step 1: Run focused R5.0 tests**

Run:

```powershell
python -m pytest tests/unit/test_organization_foundation.py tests/unit/test_init_operation.py tests/unit/test_lint_operation.py tests/unit/test_r5_0_knowledge_organization_docs.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run adjacent adapter and docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_3_claude_adapter_assets.py tests/unit/test_readme_hygiene.py tests/unit/test_release_docs.py tests/unit/test_completion_readiness_docs.py -q
```

Expected: all tests pass, with existing POSIX skips on Windows.

- [ ] **Step 3: Run full suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with existing POSIX skips on Windows.

- [ ] **Step 4: Run whitespace and dependency checks**

Run:

```powershell
git diff --check
git diff --check main..HEAD
Select-String -Path pyproject.toml -Pattern "dependencies = \\[\\]"
git ls-files .superpowers codex_doc
```

Expected:

- both `git diff --check` commands print no errors;
- `pyproject.toml` still contains `dependencies = []`;
- `git ls-files .superpowers codex_doc` prints no tracked files.

- [ ] **Step 5: Inspect branch status**

Run:

```powershell
git status -sb
git log --oneline --decorate -6
```

Expected:

- branch is `r5-0-knowledge-organization-foundation-design`;
- status is clean;
- latest commits include the R5.0 design commit and Tasks 1-4 implementation commits.

- [ ] **Step 6: Update external progress document**

Update the local progress document outside the repository:

```text
D:/ai/llmWiki/codex_doc/project_understanding_progress.md
```

Record:

- branch name;
- latest commit;
- R5.0 scope completed;
- focused, adjacent, full-suite, whitespace, dependency, and repo-hygiene verification results;
- remaining deferred work: LYT, PARA, Zettelkasten, DragonScale, semantic stale-claim lint, comparison workflows, and advanced adapter features.

- [ ] **Step 7: Commit only if verification required fixes**

If Step 1-5 required a code or doc fix, commit it:

```powershell
git add -A
git commit -m "修复 R5.0 最终验证问题"
```

If no fix was required, do not create an empty commit.
