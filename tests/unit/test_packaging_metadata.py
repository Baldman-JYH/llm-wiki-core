from __future__ import annotations

import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_limits_setuptools_package_discovery_to_core_package() -> None:
    data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    include = (
        data.get("tool", {})
        .get("setuptools", {})
        .get("packages", {})
        .get("find", {})
        .get("include")
    )

    assert include == ["llm_wiki_core*"]


def test_pyproject_exposes_llm_wiki_console_entrypoint() -> None:
    data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    scripts = data["project"]["scripts"]

    assert scripts["llm-wiki"] == "llm_wiki_core.cli:main"
