from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_transport_contract_documents_official_and_legacy_obsidian_cli() -> None:
    contract = _read("docs/transport-contract.md")

    assert "official `obsidian` CLI" in contract
    assert "legacy `obsidian-cli`" in contract
    assert "capability probe" in contract
    assert "filesystem fallback" in contract


def test_r2_report_documents_verified_boundary() -> None:
    report = _read("docs/r2-obsidian-cli-transport-report.md")

    assert "# R2 Obsidian CLI Transport Report" in report
    assert "Status: complete" in report
    assert "official `obsidian`" in report
    assert "legacy `obsidian-cli`" in report
    assert "fake runner" in report


def test_user_guide_documents_obsidian_cli_setup_without_requiring_it() -> None:
    guide = _read("docs/user-guide.md")

    assert "Obsidian CLI" in guide
    assert "filesystem fallback" in guide
    assert "not required" in guide
