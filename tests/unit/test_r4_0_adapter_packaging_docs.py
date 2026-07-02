from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


PUBLIC_DOCS = [
    "docs/adapter-packaging-plan.md",
    "docs/capability-mapping.md",
    "docs/agent-behavioral-contract.md",
    "docs/codex-command-contract.md",
    "integrations/codex/README.md",
    "integrations/codex/skills/README.md",
    "integrations/codex/plugin/README.md",
    "integrations/codex/install/README.md",
]


def test_r4_0_public_adapter_docs_have_no_damaged_text_or_private_paths() -> None:
    damaged = ["\ufffd", "闁", "娑", "閻", "闂", "濡ょ姴鐭侀惁", "Compatibility anchors"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\", r"/path/to/", r"\\path\\"]

    for relative in PUBLIC_DOCS:
        text = _read(relative)
        assert not [marker for marker in damaged if marker in text], relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"


def test_adapter_packaging_plan_documents_install_modes_and_plugin_decision() -> None:
    text = _read("docs/adapter-packaging-plan.md")

    assert "## Packaging Goals" in text
    assert "## Repo-Local Mode" in text
    assert "## User-Level Skill Mode" in text
    assert "## Plugin Packaging Decision" in text
    assert "R4.0 does not publish a marketplace-grade Codex plugin." in text
    assert "neutral core must not depend on Codex adapter behavior" in text


def test_capability_mapping_keeps_core_adapter_and_claude_boundaries() -> None:
    text = _read("docs/capability-mapping.md")

    assert "| Capability | Layer | Current status | Codex adapter behavior | Boundary |" in text
    assert "| Search durable wiki pages | Core | R3.3 complete | Map search triggers to `llm-wiki search` | Read-only; no raw-source search by default |" in text
    assert "| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Adapter-only; never neutral core |" in text


def test_agent_behavioral_contract_documents_search_and_adapter_parity() -> None:
    text = _read("docs/agent-behavioral-contract.md")

    assert "## Search Behavior" in text
    assert "Search is read-only and returns ranked durable wiki pages before query synthesis." in text
    assert "## Adapter Parity" in text
    assert "Artifact-level equivalence is required; byte-for-byte LLM prose equivalence is not required." in text
    assert "Do not treat Claude-specific hooks, commands, or subagents as neutral core requirements." in text


def test_codex_command_contract_covers_batch_and_url_ingest_without_overclaiming() -> None:
    text = _read("docs/codex-command-contract.md")

    assert "| Ingest local raw source | `ingest .raw/articles/a.md`, `process this source` | `/wiki ingest <source>` | `ingest` |" in text
    assert "| Ingest local raw folder | `ingest this folder`, `ingest .raw/articles` | `/wiki ingest-batch <source-root>` | `ingest-batch` |" in text
    assert "| Ingest one URL | `ingest this URL`, `ingest https://example.com/article` | `/wiki ingest-url <url>` | `ingest-url` |" in text
    assert "Natural-language triggers are required; slash commands are a target UX layer." in text

    assert "## `ingest` Semantics" in text
    assert "Ingest one local Markdown source under `.raw/`." in text

    assert "## `ingest-batch` Semantics" in text
    assert "Ingest a local Markdown folder or root under `.raw/`." in text
    assert "Create or update per-source wiki artifacts." in text
    assert "Update manifest, `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`." in text

    assert "## `ingest-url` Semantics" in text
    assert "Ingest one explicit URL." in text
    assert "Write an immutable snapshot under `.raw/url/` before deriving wiki artifacts." in text
    assert "No crawling, readability pipeline, JavaScript rendering, or authenticated fetch flow is included." in text

    assert "Search is read-only and returns ranked durable wiki pages before query synthesis." in text

    forbidden_claims = [
        "Claude adapter reconstruction",
        "marketplace-grade Codex plugin",
        "vector search is implemented",
        "hybrid retrieval is implemented",
        "reranking is implemented",
        "qmd integration is implemented",
        "raw-source search by default is implemented",
        "LLM synthesis is implemented",
    ]
    for claim in forbidden_claims:
        assert claim not in text


def test_codex_integration_docs_document_user_level_skill_without_global_mutation() -> None:
    readme = _read("integrations/codex/README.md")
    skills = _read("integrations/codex/skills/README.md")
    plugin = _read("integrations/codex/plugin/README.md")

    assert "Repo-local mode" in readme
    assert "User-level skill mode" in readme
    assert "does not automatically mutate global Codex configuration" in readme
    assert "Verify the skill includes `llm-wiki search`" in skills
    assert "Plugin packaging is a future target" in plugin
    assert "not a marketplace-ready plugin" in plugin


def test_roadmap_records_r4_0_release_state_and_remaining_adapter_work() -> None:
    schedule = _read("docs/roadmap-schedule.md")
    roadmap = _read("docs/roadmap.md")

    assert "### R4.0: Codex Adapter Packaging Readiness" in schedule
    assert "Status: complete." in schedule
    assert "Release: `v0.3.1-mvp`." in schedule
    assert "Codex adapter packaging readiness is complete for repo-local and documented user-level skill usage." in roadmap
    assert "Claude adapter reconstruction remains future adapter work." in roadmap
