from __future__ import annotations

from pathlib import Path


def test_codex_adapter_placeholders_exist() -> None:
    root = Path(__file__).parents[2]
    codex = root / "integrations" / "codex"

    assert (codex / "README.md").is_file()
    assert (codex / "AGENTS.template.md").is_file()
    assert (codex / "skills" / "README.md").is_file()
    assert (codex / "plugin" / "README.md").is_file()
    assert (codex / "install" / "README.md").is_file()


def test_claude_adapter_boundary_exists() -> None:
    root = Path(__file__).parents[2]
    readme = root / "integrations" / "claude" / "README.md"

    assert readme.is_file()
    assert "must stay out of the neutral core" in readme.read_text(encoding="utf-8")
