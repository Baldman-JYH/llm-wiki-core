from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_readme_is_public_project_friendly() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    forbidden_patterns = [
        r"\b[A-Z]:[\\/]",
        r"D:/",
        r"D:\\",
        r"C:/",
        r"C:\\",
        r"\\path\\to\\vault",
        r"/path/to/vault",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, readme), f"README contains local path pattern: {pattern}"

    assert "[AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)" in readme

    required_sections = [
        "## 快速开始",
        "## 使用方式",
        "## 命令速查",
        "## 文档",
        "## 当前边界",
    ]
    for section in required_sections:
        assert section in readme


def test_readme_avoids_internal_status_jargon() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    forbidden_fragments = [
        "canonical pattern",
        "full `claude-obsidian` parity",
        "preferred runtime",
        "actual read/write/search",
        "实际读写与搜索能力实现前",
        "尚未实现 Obsidian CLI 的实际读写与搜索调用",
        "D:/ai/llmWiki",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in readme

    assert "official `obsidian` CLI" in readme
    assert "filesystem fallback" in readme
    assert "验证通过" in readme
