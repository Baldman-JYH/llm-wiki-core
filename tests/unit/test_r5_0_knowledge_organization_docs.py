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
