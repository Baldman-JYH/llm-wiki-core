# Local Install Rehearsal

Date: 2026-06-26

## Purpose

Verify that a local Codex App / CLI user can install `llm-wiki-core` from the repository and run the MVP Wiki loop through the installed `llm-wiki` console entrypoint.

This rehearsal validates the artifact loop expected by the Karpathy LLM Wiki pattern: immutable raw source, maintained Markdown Wiki pages, index/log/hot updates, query with wikilink citation, saved durable insight, and lint report.

## Environment

- OS shell: Windows PowerShell
- Python install mode: editable install with `python -m pip install -e .`
- Vault transport observed: `obsidian-cli` preferred, filesystem fallback remains available
- Temporary vault: `C:\Users\ADMINI~1\AppData\Local\Temp\llm-wiki-core-m14-78075f8b9e044fc6b6cef35381e5ca26`

## Initial Finding

The first editable install attempt failed before the CLI rehearsal:

```text
error: Multiple top-level packages discovered in a flat-layout: ['integrations', 'llm_wiki_core'].
```

Root cause: setuptools automatic package discovery saw both the Python package and adapter asset directories. The fix was to explicitly limit package discovery to `llm_wiki_core*` in `pyproject.toml`, with a regression test in `tests/unit/test_packaging_metadata.py`.

## Commands Rehearsed

```powershell
python -m pip install -e .
llm-wiki --version
llm-wiki init <vault> --purpose "Milestone 14 local install rehearsal"
llm-wiki detect-transport <vault> --force
llm-wiki status <vault>
llm-wiki continue <vault>
llm-wiki ingest <vault> .raw\articles\rehearsal.md
llm-wiki query <vault> "rehearsal wiki"
llm-wiki save <vault> --title "Rehearsal Insight" --content "The local install rehearsal confirmed that the installed CLI can maintain durable wiki artifacts."
llm-wiki lint <vault>
```

## Successful Result

The second full rehearsal completed successfully through the installed `llm-wiki` entrypoint:

```text
llm-wiki-core 0.1.0
init success
detect-transport success
status success
continue success
ingest success
query success
save success
lint success
blocker: 0
high: 0
medium: 0
low: 0
```

The query returned `[[Rehearsal]]` as the cited Wiki page. The save operation created `wiki/questions/Rehearsal Insight.md`. The lint report was written to `wiki/meta/lint-report-2026-06-26.md` with no findings.

## Secondary Finding

The first complete CLI loop reached `lint success` but reported high-severity dead wikilinks for self-generated log links such as `[[Wiki Index]]`, `[[Hot Cache]]`, and `[[Overview]]`.

Root cause: lint only treated file stems as valid wikilink targets and did not recognize frontmatter `title` values. The fix now lets lint resolve both page file stems and frontmatter titles.

## Cleanup Notes

Editable installation generated `llm_wiki_core.egg-info` in the repository. CLI and pytest runs generated `__pycache__` folders. These are generated artifacts and should not be treated as source changes.

