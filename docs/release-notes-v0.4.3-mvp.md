# Release Notes: v0.4.3-mvp

Date: 2026-07-03

## Status

`v0.4.3-mvp` marks the R4.3 Claude Local Adapter MVP release for `llm-wiki-core`.

This release keeps the neutral core unchanged and adds project-local Claude adapter assets for local Claude Code use. It maps `/wiki` and `/save` intent to the same neutral `llm-wiki` commands already used by the core and Codex adapter path.

## Included

- Project-local Claude adapter assets.
- `CLAUDE.template.md` project instructions.
- `skills/llm-wiki/SKILL.md` Claude skill.
- Thin `commands/wiki.md` and `commands/save.md` wrappers.
- PowerShell project-local installer: `install.ps1`.
- POSIX project-local installer: `install.sh`.
- Dry-run support for Claude project-local installation.
- Conservative replace behavior with explicit replace flags.
- Public install documentation and Claude adapter plan.
- Capability mapping and roadmap guardrails for R4.3.
- Repository hygiene guard against tracked `.superpowers` or `codex_doc` scratch files.

## Not Included

- This release does not edit user-global Claude settings automatically.
- active Claude hooks remain deferred.
- Claude subagents remain deferred.
- .claude-plugin packaging remains deferred.
- Autoresearch remains deferred.
- Canvas workflows remain deferred.
- Hybrid retrieval, vector search, reranking, and qmd integration remain deferred.
- DragonScale or log-folding memory remains deferred.
- Methodology modes remain deferred.
- Automatic Git commits remain deferred.
- Full `claude-obsidian` parity is not claimed.

## Verification

Release verification before publication:

```powershell
python -m pytest tests/unit/test_r4_3_claude_adapter_assets.py -q
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_0_adapter_packaging_docs.py tests/unit/test_integration_skeleton.py -q
python -m pytest -q
git diff --check
```

Expected result for this release line:

```text
16 passed, 4 skipped
20 passed
248 passed, 10 skipped
```

The skipped tests are POSIX shell execution checks that are expected on Windows. They do not require Windows users to install WSL or Git Bash.

## Release Tag

Local and remote release tag:

```text
v0.4.3-mvp
```

## Archive

The release archive should be produced from the Git tag with `git archive` and stored outside the repository working tree.
