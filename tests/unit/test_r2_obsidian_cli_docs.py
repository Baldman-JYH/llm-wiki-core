from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DOCS = (
    "README.md",
    "docs/user-guide.md",
    "docs/transport-contract.md",
    "docs/r2-obsidian-cli-transport-report.md",
    "docs/roadmap.md",
    "docs/completion-criteria.md",
    "docs/release-readiness-checklist.md",
    "docs/artifact-equivalence-verification.md",
    "docs/obsidian-cli-transport-boundary-rehearsal.md",
    "docs/reference-implementation-alignment.md",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _public_docs_corpus() -> str:
    return "\n".join(_read(relative) for relative in PUBLIC_DOCS)


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
    assert "Actual Obsidian CLI read/write/search is not implemented." not in guide


def test_public_docs_avoid_local_absolute_paths() -> None:
    corpus = _public_docs_corpus()

    assert re.search(r"\b[A-Za-z]:[\\/]", corpus) is None


def test_public_docs_keep_karpathy_claude_and_neutral_core_framing() -> None:
    corpus = _public_docs_corpus()
    lower = corpus.lower()

    assert "karpathy" in lower
    assert "gist" in lower
    assert "claude-obsidian" in lower
    assert ("reference implementation" in lower) or ("参考实现" in corpus)
    assert "llm-wiki-core" in lower
    assert ("neutral" in lower) or ("中性核心" in corpus) or ("中性" in corpus)


def test_public_docs_do_not_claim_r2_obsidian_runtime_is_unimplemented() -> None:
    corpus = _public_docs_corpus()
    stale_fragments = [
        "Actual Obsidian CLI read/write/search is not implemented",
        "actual Obsidian CLI read/write/search is not implemented",
        "actual read/write/search through Obsidian CLI remains outside the MVP",
        "actual read/write/search 实现前不作为 runtime preferred",
        "Actual Obsidian CLI read / write / search integration",
        "Obsidian CLI actual read/write/search",
    ]

    for fragment in stale_fragments:
        assert fragment not in corpus


def test_public_docs_describe_obsidian_cli_as_optional_verified_runtime() -> None:
    corpus = _public_docs_corpus()

    assert "official `obsidian` CLI" in corpus
    assert "filesystem fallback" in corpus
    assert "read/write/append/list/search" in corpus
    assert "capability probe" in corpus
    assert "legacy `obsidian-cli`" in corpus
