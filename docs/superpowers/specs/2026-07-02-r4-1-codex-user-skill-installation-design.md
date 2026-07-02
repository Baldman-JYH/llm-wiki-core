# R4.1 Codex User-Level Skill Installation Design

Date: 2026-07-02

## Summary

R4.1 should turn the R4.0 documented Codex user-level skill path into an explicit, verifiable, and conservative local installation workflow.

The goal is not to publish a marketplace-grade plugin and not to mutate Codex global configuration automatically. The goal is to help a local Codex App or Codex CLI user install the reusable `llm-wiki` skill into the documented Codex user skill location only when they explicitly ask for that operation.

## Source Of Truth

The design follows the current Codex manual sections on Agent Skills, `AGENTS.md`, and plugin packaging:

- Skills are directories with `SKILL.md` plus optional scripts and references.
- Codex scans repository, user, admin, and system skill locations.
- The documented user skill location is `$HOME/.agents/skills`.
- Plugins are the distribution unit for broader sharing; direct skill folders remain best for local authoring and personal workflows.
- Skills can be enabled or disabled through Codex configuration, but R4.1 must not edit global Codex configuration automatically.

## Why R4.1 Comes Next

R4.0 made Codex adapter packaging readable and guarded. It did not yet make user-level skill installation executable.

R4.1 has the best risk-to-value ratio because:

- It directly improves the local Codex App and Codex CLI user experience.
- It keeps adapter behavior outside the neutral core.
- It is smaller than Claude adapter reconstruction.
- It strengthens the same path R4.0 just documented.
- It can be tested with filesystem fixtures and dry-run output without requiring a live Codex app session.

## Non-Goals

R4.1 must not implement:

- marketplace-grade Codex plugin publication;
- Claude adapter reconstruction;
- Claude Code commands, hooks, or subagents;
- automatic global Codex configuration edits;
- automatic installation without an explicit user flag;
- vector search, hybrid retrieval, reranking, qmd integration, raw-source search by default, or LLM synthesis;
- changes to neutral core operation behavior.

## User Experience

### Repo-Local Baseline

Repo-local install remains unchanged. A user can still initialize a vault from the repository with the existing install scripts and use the checked-in `integrations/codex` assets.

### Explicit User-Level Skill Install

R4.1 adds an explicit user-level skill installation path:

```powershell
integrations/codex/install/install.ps1 -InstallUserSkill -DryRun
integrations/codex/install/install.ps1 -InstallUserSkill
```

```sh
integrations/codex/install/install.sh --install-user-skill --dry-run
integrations/codex/install/install.sh --install-user-skill
```

The command should:

1. locate `integrations/codex/skills/llm-wiki`;
2. validate that `SKILL.md` exists and includes `name` and `description`;
3. resolve the user skill destination from the current user home directory;
4. print source, destination, and planned file operations;
5. copy the skill directory only when the explicit install flag is present and dry-run is not active;
6. refuse to overwrite an existing different destination unless an explicit replace flag is provided;
7. print verification prompts that work in Codex App and Codex CLI.

The default install behavior should not change global Codex state.

## Destination Policy

R4.1 should use portable user-home semantics:

- POSIX-like systems: `$HOME/.agents/skills/llm-wiki`
- Windows PowerShell: `$HOME\.agents\skills\llm-wiki`

Docs may show these symbolic home-relative examples. They must not include private absolute paths.

The installer should support an override destination for tests and advanced users:

- PowerShell: `-SkillDestination <path>`
- Shell: `--skill-destination <path>`

The override is also useful for hermetic tests.

## Replace Policy

R4.1 should be conservative:

- If the destination does not exist, copy the skill directory.
- If the destination exists and appears identical, report that it is already installed.
- If the destination exists and differs, fail by default with a clear message.
- If a replace flag is supplied, replace only the target `llm-wiki` skill directory, never a parent directory.
- Do not delete unrelated files.
- Do not edit `~/.codex/config.toml`.

An uninstall command is optional for R4.1. If included, it must be explicit and must only remove a destination previously recognized as the `llm-wiki` skill.

## Verification Policy

R4.1 should verify the installed skill by inspecting files, not by requiring Codex to reload skills during tests.

Installer verification should check:

- destination `SKILL.md` exists;
- copied `SKILL.md` contains the current command coverage;
- no private absolute paths are written into docs or test fixtures;
- dry-run does not create files;
- replace behavior is explicit;
- platform-specific scripts stay thin and call the same conceptual workflow.

User-facing verification can ask the user to start a new Codex App / CLI session and use natural-language triggers such as:

- "check wiki status"
- "continue wiki"
- "search wiki for durable knowledge"
- "what does the wiki know about durable knowledge"

## File Scope

Expected implementation files:

- `integrations/codex/install/install.ps1`
- `integrations/codex/install/install.sh`
- `integrations/codex/install/README.md`
- `integrations/codex/README.md`
- `integrations/codex/skills/README.md`
- `docs/adapter-packaging-plan.md`
- `docs/roadmap-schedule.md`
- `tests/unit/test_codex_installer_smoke.py`
- `tests/unit/test_r4_1_user_skill_install_docs.py`
- optional helper tests if the existing installer tests become too large

Neutral core Python operation files should not be touched.

## Testing Strategy

R4.1 should use TDD.

Minimum focused tests:

- PowerShell dry-run user skill install prints source, destination, and planned action without writing files.
- Shell dry-run user skill install prints equivalent output without writing files.
- PowerShell user skill install copies the skill into a fixture destination.
- Shell user skill install copies the skill into a fixture destination on non-Windows platforms.
- Existing destination with different content fails unless replace is explicit.
- Docs mention `$HOME/.agents/skills` without private absolute paths.
- Docs state that global Codex configuration is not edited automatically.
- Guard tests keep plugin marketplace publication and Claude adapter reconstruction deferred.

Full suite must pass before merge.

## Compatibility

Windows support must be native PowerShell and must not require WSL or Git Bash.

macOS and Linux support should use the existing shell installer.

The installation workflow should work even when Codex is not currently running. Reloading skills is a user/session concern, not something tests should require.

## Risks

### Risk: accidental global mutation

Mitigation: user-level install is explicit, dry-run is available, and no global config is edited automatically.

### Risk: overwriting a user's existing skill

Mitigation: existing different destinations fail by default and require an explicit replace flag.

### Risk: docs drift from Codex skill discovery

Mitigation: tests guard `$HOME/.agents/skills`, current command coverage, and no private paths.

### Risk: Windows path assumptions

Mitigation: use PowerShell home-relative paths and fixture overrides in tests.

## Acceptance Criteria

R4.1 is complete when:

- user-level skill installation is explicit, documented, and dry-run capable;
- repo-local install remains unchanged;
- installed skill artifacts are verifiable by tests;
- existing different destinations are not overwritten by default;
- no global Codex configuration is edited automatically;
- plugin publication remains deferred;
- Claude adapter reconstruction remains deferred;
- neutral core behavior is unchanged;
- focused R4.1 tests and the full test suite pass.
