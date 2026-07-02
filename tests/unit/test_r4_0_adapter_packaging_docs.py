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
    "integrations/codex/README.md",
    "integrations/codex/skills/README.md",
    "integrations/codex/plugin/README.md",
    "integrations/codex/install/README.md",
]


def test_r4_0_public_adapter_docs_have_no_damaged_text_or_private_paths() -> None:
    damaged = ["\ufffd", "閿?", "閳?", "閹?", "閵?", "涔?", "鐞?", "闂?", "閻?", "妤犲矁鐦?"]
    private_path_patterns = [r"\b[A-Z]:[\\/]", r"D:/", r"D:\\", r"C:/", r"C:\\"]

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
