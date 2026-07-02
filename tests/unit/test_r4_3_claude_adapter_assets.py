from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


CLAUDE_PUBLIC_DOCS = [
    "integrations/claude/README.md",
    "integrations/claude/CLAUDE.template.md",
    "integrations/claude/skills/README.md",
    "integrations/claude/skills/llm-wiki/SKILL.md",
    "integrations/claude/commands/wiki.md",
    "integrations/claude/commands/save.md",
]

DAMAGED_TEXT_SENTINELS = (
    "\ufffd",
    "闂?,",
    "濞?,",
    "闁?,",
    "闂?,",
    "婵°倗濮撮惌渚€鎯?",
)


def _find_damaged_markers(text: str) -> list[str]:
    return [marker for marker in DAMAGED_TEXT_SENTINELS if marker in text]


def test_r4_3_claude_assets_exist_and_are_project_local() -> None:
    expected = [
        "integrations/claude/CLAUDE.template.md",
        "integrations/claude/skills/README.md",
        "integrations/claude/skills/llm-wiki/SKILL.md",
        "integrations/claude/commands/wiki.md",
        "integrations/claude/commands/save.md",
    ]

    for relative in expected:
        assert (ROOT / relative).is_file(), relative

    readme = _read("integrations/claude/README.md")
    assert "R4.3 local adapter MVP" in readme
    assert "project-local" in readme
    assert "does not edit user-global Claude settings automatically" in readme


def test_claude_skill_frontmatter_and_command_mapping() -> None:
    text = _read("integrations/claude/skills/llm-wiki/SKILL.md")

    assert "name: llm-wiki" in text
    assert "description:" in text
    assert "Claude local adapter MVP" in text
    assert "llm-wiki init <vault> --purpose" in text
    assert "llm-wiki continue <vault>" in text
    assert "llm-wiki detect-transport <vault>" in text
    assert "llm-wiki status <vault>" in text
    assert "llm-wiki ingest <vault> <source>" in text
    assert "llm-wiki ingest-batch <vault> <source-root>" in text
    assert "llm-wiki ingest-url <vault> <url>" in text
    assert "llm-wiki search <vault>" in text
    assert "llm-wiki query <vault>" in text
    assert "llm-wiki save <vault> --title" in text
    assert "llm-wiki lint <vault>" in text
    assert "Do not modify `.raw/` files." in text
    assert "Do not reimplement neutral core file-writing behavior in prompt text." in text


def test_claude_template_documents_llm_wiki_rules() -> None:
    text = _read("integrations/claude/CLAUDE.template.md")

    assert "# LLM Wiki Claude Project Instructions" in text
    assert "Karpathy's LLM Wiki gist is the canonical abstract pattern." in text
    assert "`AgriciDaniel/claude-obsidian` is a reference implementation case" in text
    assert "Use the project-local Claude `llm-wiki` skill" in text
    assert "Raw sources under `.raw/` are immutable." in text
    assert "Artifact-level parity is required." in text
    assert "Byte-for-byte prose parity is not required." in text
    assert "Do not claim full `claude-obsidian` parity." in text


def test_claude_command_wrappers_are_thin() -> None:
    wiki = _read("integrations/claude/commands/wiki.md")
    save = _read("integrations/claude/commands/save.md")

    assert "Read the project-local `llm-wiki` skill" in wiki
    assert "Map `/wiki` intent to neutral `llm-wiki` commands" in wiki
    assert "Do not implement hooks, subagents, or Obsidian-specific automation." in wiki
    assert "Read the project-local `llm-wiki` skill" in save
    assert 'Map `/save` intent to `llm-wiki save <vault> --title "..." --content "..."`.' in save
    assert "Do not save chat noise." in save


def test_r4_3_claude_assets_defer_high_risk_surfaces() -> None:
    combined = "\n".join(_read(relative) for relative in CLAUDE_PUBLIC_DOCS).lower()

    required_deferred = [
        "active claude hooks are deferred",
        "claude subagents are deferred",
        ".claude-plugin packaging is deferred",
        "autoresearch is deferred",
        "canvas workflows are deferred",
        "dragonscale memory is deferred",
        "methodology modes are deferred",
        "automatic git commits are deferred",
    ]
    for phrase in required_deferred:
        assert phrase in combined

    forbidden_claims = [
        "full claude-obsidian parity is complete",
        "active claude hooks are enabled",
        "claude subagents are enabled",
        "autoresearch is implemented",
        "canvas workflows are implemented",
        "dragonscale memory is implemented",
        "automatic git commits are enabled",
    ]
    for phrase in forbidden_claims:
        assert phrase not in combined


def test_r4_3_claude_assets_do_not_ship_active_hooks_subagents_or_plugin() -> None:
    forbidden_paths = [
        "integrations/claude/hooks/hooks.json",
        "integrations/claude/.claude/settings.json",
        "integrations/claude/.claude-plugin/plugin.json",
        "integrations/claude/agents/wiki-ingest.md",
        "integrations/claude/agents/wiki-lint.md",
        "integrations/claude/agents/verifier.md",
    ]

    for relative in forbidden_paths:
        assert not (ROOT / relative).exists(), relative


def test_r4_3_public_docs_have_no_private_paths_or_damaged_text() -> None:
    private_path_patterns = [r"\b[A-Z]:[\\/]", "D:" + "/", "D:" + "\\\\", "C:" + "/", "C:" + "\\\\"]

    for relative in CLAUDE_PUBLIC_DOCS:
        text = _read(relative)
        assert not _find_damaged_markers(text), relative
        for pattern in private_path_patterns:
            assert not re.search(pattern, text), f"{relative} contains {pattern}"
