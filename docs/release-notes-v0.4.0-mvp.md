# Release Notes: v0.4.0-mvp

Date: 2026-07-02

## Status

`v0.4.0-mvp` marks the R4.1 Codex User-Level Skill Installation release for `llm-wiki-core`.

This release keeps the neutral core unchanged and improves the local Codex App / Codex CLI adapter path. It turns the previously documented Codex user-level skill mode into an explicit, dry-run-capable local installation workflow.

## Included

- PowerShell user-level skill install with `-InstallUserSkill`.
- POSIX shell user-level skill install with `--install-user-skill`.
- Default user skill destination documentation for `$HOME/.agents/skills/llm-wiki`.
- Dry-run support for user-level skill install commands.
- Destination override support for tests and advanced local installs.
- Conservative replace behavior with explicit replace flags.
- Safety guards before destructive replacement of an existing skill directory.
- Guard tests for installer behavior, public docs, R4.1 plan hygiene, and deferred boundaries.
- Documentation that repo-local install remains available.

## Not Included

- R4.1 does not edit global Codex configuration automatically.
- marketplace-grade Codex plugin publication remains deferred.
- Claude adapter reconstruction remains deferred.
- Claude Code commands, hooks, and subagents remain adapter-only future work.
- Neutral core operations are not changed by this release.

## Verification

Release verification before publication:

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py tests/unit/test_r4_1_user_skill_install_docs.py -q
python -m pytest -q
git diff --check
```

Expected result for this release line:

```text
16 passed, 6 skipped
220 passed, 6 skipped
```

The skipped tests are POSIX shell execution checks that are expected on Windows. They do not require Windows users to install WSL or Git Bash.

## Release Tag

Local and remote release tag:

```text
v0.4.0-mvp
```

## Archive

The release archive should be produced from the Git tag with `git archive` and stored outside the repository working tree.
