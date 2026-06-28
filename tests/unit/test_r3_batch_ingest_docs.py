from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
KNOWN_MOJIBAKE_SAMPLES = (
    "鏈湴 Markdown",
    "閺堫剙婀?Markdown",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _assert_no_known_mojibake_samples(name: str, text: str) -> None:
    found_samples = [sample for sample in KNOWN_MOJIBAKE_SAMPLES if sample in text]
    assert not found_samples, f"{name} contains known mojibake samples: {', '.join(found_samples)}"


def test_readme_documents_ingest_batch_command_and_positioning() -> None:
    readme = _read("README.md")

    assert "ingest-batch" in readme
    assert "llm-wiki ingest-batch <vault> .raw/articles" in readme
    assert "local Markdown" in readme
    _assert_no_known_mojibake_samples("README.md", readme)

    assert "Karpathy" in readme
    assert "abstract idea" in readme
    assert "AgriciDaniel/claude-obsidian" in readme
    assert "Claude Code + Obsidian" in readme
    assert "neutral" in readme
    assert "practice implementation" in readme
    assert "does not claim full parity with `claude-obsidian`" in readme
    assert "full `claude-obsidian` parity" not in readme


def test_user_guide_documents_positioning_and_r3_1_boundaries() -> None:
    guide = _read("docs/user-guide.md")

    assert "llm-wiki ingest-batch <vault> .raw/articles" in guide
    assert "--force" in guide
    assert "--json" in guide
    _assert_no_known_mojibake_samples("docs/user-guide.md", guide)

    assert "Karpathy's LLM Wiki pattern" in guide
    assert "reference implementation for the Claude Code + Obsidian workflow" in guide
    assert "neutral LLM Wiki practice implementation" in guide
    assert "Full `claude-obsidian` parity is not claimed." in guide

    assert "R3.1 supports local Markdown batch ingest for `.md` files" in guide
    assert "URL ingest" in guide
    assert "HTML cleanup" in guide
    assert "vector search" in guide
    assert "LLM synthesis" in guide
    assert "outside R3.1" in guide

    assert "R3.1 includes URL ingest" not in guide
    assert "R3.1 includes HTML cleanup" not in guide
    assert "R3.1 includes vector search" not in guide
    assert "R3.1 includes LLM synthesis" not in guide


def test_roadmap_schedule_records_r3_1_batch_ingest_status_and_future_boundary() -> None:
    schedule = _read("docs/roadmap-schedule.md")

    assert "R3.1: Batch Ingest" in schedule
    assert "Status: complete." in schedule
    assert "local `.md` files under `.raw/`" in schedule
    assert "URL ingest" in schedule
    assert "HTML cleanup" in schedule
    assert "vector search" in schedule
    assert "LLM synthesis" in schedule
    assert "future R3" in schedule
    assert "Full `claude-obsidian` parity is not claimed in R3.1." in schedule
    _assert_no_known_mojibake_samples("docs/roadmap-schedule.md", schedule)
