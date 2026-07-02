# R4.0 Codex Adapter Packaging Readiness Design

## Status

Approved for design by the user on 2026-07-02.

## Context

`llm-wiki-core` has reached `v0.2.0-mvp` with R3.3 Retrieval Foundation merged into `main`. The neutral core now supports local vault initialization, local file ingest, batch ingest, URL ingest, status/continue, lint, save, query, and read-only search over durable Markdown wiki pages.

The next roadmap section is R4 Adapter Expansion. The long-term R4 scope includes:

- Codex user-level skill packaging;
- Codex plugin packaging decision;
- Claude adapter reconstruction;
- Claude commands, hooks, and subagents as adapter-only behavior.

R4 should not start by rebuilding the Claude adapter. The immediate product risk is that Codex users still do not have a polished, documented, repeatable adapter installation and activation path. Some public and adapter-facing documents also still contain legacy damaged text or stale command mappings from earlier MVP work. If packaging starts before those surfaces are cleaned, the packaging work will amplify confusing documentation.

R4.0 should therefore be a readiness slice: make the Codex adapter usable, documented, and verifiable without changing the neutral core behavior.

## Goals

R4.0 should provide a clean Codex adapter readiness layer:

1. Make public project docs readable and open-source friendly.
2. Remove README compatibility anchors that preserve damaged historical text.
3. Update Codex adapter docs to include R3.3 `search` behavior.
4. Update the Codex skill draft to map natural-language search triggers to `llm-wiki search`.
5. Define user-level skill packaging as a documented, testable install mode.
6. Keep repo-local installation as the baseline install mode.
7. Keep Codex plugin packaging as a decision record and future packaging target, not an R4.0 implementation requirement.
8. Add guard tests that prevent stale command mappings, local path leaks, damaged text, and core/adapter boundary drift.
9. Preserve `dependencies = []`.
10. Preserve all R3.3 core behavior.

## Non-Goals

R4.0 does not implement:

- Claude adapter reconstruction;
- Claude Code commands, hooks, subagents, or `.claude-plugin` generation;
- marketplace-grade Codex plugin publication;
- automatic global Codex configuration mutation;
- Codex Web or remote execution support;
- new neutral core operations;
- new retrieval behavior;
- vector search, hybrid retrieval, reranking, qmd integration, or LLM synthesis;
- Obsidian CLI runtime changes.

Those remain possible later R4 or R5 nodes.

## Recommended Approach

Use a documentation-and-packaging-readiness slice.

This is preferred over starting with Claude adapter reconstruction because the project's current goal is to let Codex App and Codex CLI users achieve the same core LLM Wiki maintenance effect as the Claude Code + Obsidian reference workflow. A polished Codex adapter path is the shortest path to that outcome.

This is also preferred over implementing marketplace plugin packaging immediately. The repository already has repo-local installers and a skill draft. R4.0 should first make those assets correct, complete, and testable. Plugin packaging can then become a smaller decision once the adapter content is stable.

## Adapter Layers

R4.0 should keep three adapter layers distinct:

```text
neutral core
  owns operations, schema, transport contracts, validation, CLI behavior

repo-local Codex adapter
  owns AGENTS template, command mapping docs, install scripts, local verification

user-level Codex skill package
  owns reusable skill content and installation instructions for a user's Codex environment
```

The neutral core must not gain Codex-specific behavior. The Codex adapter may call core commands and describe how Codex should trigger them.

## Documentation Hygiene

R4.0 should clean public and adapter-facing docs enough that a new GitHub user can understand the project without reading historical implementation notes.

Primary cleanup targets:

- `README.md`
- `docs/adapter-packaging-plan.md`
- `docs/capability-mapping.md`
- `docs/agent-behavioral-contract.md`
- `integrations/codex/README.md`
- `integrations/codex/COMMANDS.md`
- `integrations/codex/skills/README.md`
- `integrations/codex/plugin/README.md`

README should use one language consistently for prose. English is preferred for open-source readability because most current operation docs and CLI contracts are already English. Specific project names may remain English even if a future Chinese companion guide is added.

R4.0 should remove or replace damaged compatibility anchors in README. Tests should assert real readable section names instead of preserving mojibake headings.

Historical specs and plans do not need to be rewritten wholesale unless they are linked as public entry points. If a document is retained as historical design material, it may remain under `docs/superpowers/`. Public README links should point users to current readable docs first.

## Codex Skill Contract

The Codex skill draft at `integrations/codex/skills/llm-wiki/SKILL.md` should reflect current core commands:

- `init`
- `detect-transport`
- `status`
- `continue`
- `ingest`
- `ingest-batch`
- `ingest-url`
- `search`
- `query`
- `save`
- `lint`

Natural-language triggers should include:

- "set up wiki" or "scaffold vault" -> `init`
- "check transport" -> `detect-transport`
- "check wiki status" -> `status`
- "continue wiki" or "resume wiki context" -> `continue`
- "ingest this source" -> `ingest`
- "ingest this folder" -> `ingest-batch`
- "ingest this URL" -> `ingest-url`
- "search wiki for X" or "find wiki pages about X" -> `search`
- "what does the wiki know about X" -> `query`
- "save this insight" -> `save`
- "lint the wiki" -> `lint`

The skill should state that `search` is read-only and returns ranked durable wiki pages before query synthesis.

## Command Mapping Contract

`integrations/codex/COMMANDS.md` should match `docs/codex-command-contract.md` at the adapter level. It does not need to duplicate every core operation detail, but it must include:

- natural-language trigger;
- target slash command where applicable;
- core CLI command;
- mutation behavior;
- key files read or written.

R4.0 should make command mappings current with R3.3. `search` must be present.

## Installation Modes

R4.0 should document two install modes:

### Repo-Local Mode

Repo-local mode remains the baseline:

```powershell
integrations/codex/install/install.ps1 -VaultPath <vault> -Purpose "..."
```

```sh
integrations/codex/install/install.sh <vault> "..."
```

This mode installs the local editable package, initializes the vault, detects transport, and prints re-entry commands.

### User-Level Skill Mode

User-level skill mode should be documented as a reusable installation option for Codex users. R4.0 should not mutate a user's global Codex configuration automatically. Instead it should provide:

- a source directory to copy from;
- destination examples for Windows and macOS/Linux;
- dry-run commands where possible;
- verification steps that confirm the skill content includes current command mappings.

If a helper script is added, it must support dry-run first and must not overwrite existing user files without explicit force behavior. The first implementation plan may choose docs-only user-level packaging if that is enough to establish the contract.

## Plugin Packaging Decision

R4.0 should produce a clear plugin packaging decision, but not a marketplace-ready plugin.

The decision should answer:

- whether plugin packaging is a near-term target;
- which files would belong to a future plugin;
- which behavior remains in the neutral core;
- which behavior remains in the Codex adapter;
- what is still blocked by official Codex plugin conventions or distribution policy.

This decision may live in `docs/adapter-packaging-plan.md` or a new ADR if the trade-off is substantial enough.

## Guard Tests

R4.0 should add or update tests for:

- README has readable public section headings.
- README has no local absolute paths.
- README references Karpathy's gist and `AgriciDaniel/claude-obsidian` correctly.
- README does not claim full `claude-obsidian` parity.
- README does not contain replacement characters, known damaged-text markers, or historical compatibility anchors.
- Codex skill includes current commands, including `search`, `ingest-batch`, and `ingest-url`.
- Codex skill maps natural-language search triggers.
- Codex command mapping includes `search` and read-only behavior.
- Install scripts retain dry-run behavior.
- Adapter packaging docs keep core and adapter responsibilities separate.

Tests should check behavior and user-facing contract, not only keyword fragments.

## Data Flow

Repo-local onboarding:

1. User installs the package or runs the repo-local installer.
2. Installer runs `llm-wiki init`.
3. Installer runs `llm-wiki detect-transport`.
4. User opens the vault in Codex App or works from Codex CLI.
5. Codex reads `AGENTS.md` and/or the user-level skill.
6. Codex maps natural language to core CLI operations.
7. Core operations maintain `.raw/`, `wiki/`, and deterministic metadata.

User-level skill onboarding:

1. User installs or copies the skill into the Codex user skills directory.
2. User opens a vault or project that uses `llm-wiki-core`.
3. Codex skill discovery exposes LLM Wiki behavior.
4. User can say "search wiki for X", "ingest this URL", or "continue wiki".
5. Codex follows the adapter contract and invokes core commands.

## Error Handling

R4.0 should document and test user-facing failure modes:

- installer dry-run must not create a vault;
- install docs must not assume WSL or Git Bash on Windows;
- user-level skill install docs must not overwrite existing files by default;
- command mapping must not imply slash commands are mandatory;
- plugin docs must not imply marketplace support already exists.

## Testing Strategy

R4.0 should use focused tests before implementation:

- documentation guard tests for README readability and hygiene;
- adapter asset tests for skill and command mapping completeness;
- installer smoke tests for dry-run behavior;
- release/documentation tests if public docs are updated;
- full test suite before merge.

Existing R3 tests should remain green.

## Acceptance Criteria

R4.0 is complete when:

1. README is readable, public-friendly, and free of damaged compatibility anchors.
2. Current public docs describe `v0.2.0-mvp` and R3.3 search accurately.
3. Codex skill content includes `search`, `ingest-batch`, and `ingest-url`.
4. Codex command mapping includes search and read-only retrieval behavior.
5. Repo-local install docs remain valid on Windows and macOS/Linux.
6. User-level skill packaging is documented with verification steps.
7. Plugin packaging has a clear decision and remains non-blocking.
8. Guard tests prevent stale adapter command mappings and damaged README text.
9. No runtime dependency is added.
10. Full tests pass.

## Deferred Follow-Up

After R4.0, possible R4 follow-ups:

- R4.1: implement user-level skill install helper with dry-run and force modes;
- R4.2: Codex plugin manifest prototype if official conventions are stable enough;
- R4.3: Claude adapter reconstruction as adapter-only files;
- R4.4: cross-adapter parity fixture runner;
- R5: knowledge organization modes and advanced retrieval.
