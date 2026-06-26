from __future__ import annotations

from pathlib import Path


def test_fixture_directories_exist() -> None:
    root = Path(__file__).parents[1] / "fixtures"

    expected = {
        "f0-empty",
        "f1-fresh-vault",
        "f2-single-source",
        "f3-existing-knowledge",
        "f4-broken-wiki",
    }

    actual = {path.name for path in root.iterdir() if path.is_dir()}
    assert expected.issubset(actual)


def test_each_fixture_has_readme() -> None:
    root = Path(__file__).parents[1] / "fixtures"

    for fixture in [
        "f0-empty",
        "f1-fresh-vault",
        "f2-single-source",
        "f3-existing-knowledge",
        "f4-broken-wiki",
    ]:
        assert (root / fixture / "README.md").is_file()
