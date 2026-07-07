from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_knowledge_organization_doc_tracks_r5_1_route_adoption() -> None:
    text = _read("docs/knowledge-organization.md")

    assert "R5.1 adds organization route adoption" in text
    assert "ingest, batch ingest, save, search, and status read routes from the organization contract" in text
    assert "R5.1 does not add non-generic organization modes" in text


def test_capability_mapping_tracks_route_adoption_without_methodology_claims() -> None:
    text = _read("docs/capability-mapping.md")

    assert "| Organization route adoption | Core | R5.1 complete |" in text
    assert "| Methodology modes | Deferred extension | Deferred |" in text
    assert "| DragonScale or log-folding memory | Deferred extension | Deferred |" in text


def test_roadmap_documents_r5_1_route_adoption_and_future_modes() -> None:
    roadmap = _read("docs/roadmap.md")
    schedule = _read("docs/roadmap-schedule.md")

    assert "R5.1 organization route adoption is complete" in roadmap
    assert "generic remains the default organization mode" in roadmap
    assert "### R5.1: Organization Route Adoption Foundation" in schedule
    assert "Status: complete." in schedule
    assert "Non-generic organization modes remain future R5.x work." in schedule


def test_r5_1_docs_do_not_claim_advanced_modes_are_complete() -> None:
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
        "non-generic organization modes are complete",
    ]
    for phrase in forbidden:
        assert phrase not in combined
