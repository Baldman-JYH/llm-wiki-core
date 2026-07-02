# R4.3 Claude Local Adapter MVP Design

Date: 2026-07-02

## Summary

R4.3 should design the first local Claude Code adapter implementation slice for `llm-wiki-core`.

The goal is to let a local Claude Code user drive the same durable Markdown Wiki outcomes that R4.2 defined for Codex and Claude parity, without copying the full `AgriciDaniel/claude-obsidian` implementation and without moving Claude-specific behavior into the neutral core.

R4.3 should be a local adapter MVP. It should focus on project-level Claude instructions and command/skill entry points for `/wiki` and `/save`, because those map directly to existing neutral core operations. Hooks, subagents, `.claude-plugin`, `autoresearch`, `canvas`, hybrid retrieval, DragonScale, methodology modes, automatic Git commits, and remote Claude/Codex surfaces remain out of scope unless separately designed.

## Source Of Truth

The canonical abstraction remains Karpathy's LLM Wiki gist:

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

The reference implementation case remains `AgriciDaniel/claude-obsidian`:

https://github.com/AgriciDaniel/claude-obsidian

The current Claude Code adapter design also follows the public Claude Code documentation checked during R4.3 exploration:

- Claude Code skills can define slash-style invocations through `SKILL.md`, and custom command files under `.claude/commands/` continue to work.
- Project settings live under `.claude/` and can be shared with collaborators.
- `CLAUDE.md` gives persistent project instructions, but it is context guidance, not a hard enforcement mechanism.
- Hooks are lifecycle automation and can enforce or mutate behavior, so R4.3 must not enable mutating hooks by default.
- Subagents are a Claude Code adapter surface and must remain outside neutral core.

## Why R4.3 Comes Next

R4.2 established the parity contract but did not ship Claude-facing assets. The next smallest valuable step is to make Claude Code able to discover the LLM Wiki workflow locally while preserving the R4.2 boundaries.

R4.3 should not attempt full `claude-obsidian` parity. The reference implementation includes `/autoresearch`, `/canvas`, auto-commit hooks, hot-cache hooks, parallel ingest subagents, Obsidian-specific setup, methodology modes, and DragonScale memory behavior. Those are useful, but they are independent extension tracks with higher risk and larger verification needs.

## User Experience

The R4.3 MVP should support a local Claude Code user who has a checked-out `llm-wiki-core` project or a project that has copied the adapter assets.

Expected local experience:

1. User installs or copies the Claude adapter assets into a target project or vault.
2. Claude Code loads project guidance from `CLAUDE.md` or `.claude/CLAUDE.md`.
3. User can invoke `/wiki` or a skill-backed equivalent to initialize, continue, check status, ingest, search, query, or lint via neutral `llm-wiki` commands.
4. User can invoke `/save` or a skill-backed equivalent to save durable knowledge via neutral `llm-wiki save`.
5. Claude sees clear rules that raw sources under `.raw/` are immutable, generated wiki pages are durable artifacts, and byte-for-byte prose parity is not required.

The user should not need Obsidian, Claude hooks, Claude subagents, or a plugin marketplace install for the R4.3 MVP.

## Adapter Surface Choice

R4.3 should prefer Claude Code skills as the canonical local adapter surface.

Reasons:

- Claude Code documentation says skills follow the Agent Skills open standard and can be invoked directly with slash-style names.
- Skills can carry instructions plus optional support files without bloating always-loaded context.
- Codex already uses a skill-based adapter, so a Claude skill keeps the cross-agent adapter model conceptually aligned.

R4.3 may also include lightweight `.claude/commands/wiki.md` and `.claude/commands/save.md` compatibility wrappers if tests and docs make clear that the skill is the canonical source and command files are thin entry points. If this adds too much implementation risk, command wrappers should be deferred to R4.4.

## Proposed Files

The future implementation plan should create or update these adapter assets:

- `integrations/claude/CLAUDE.template.md`
- `integrations/claude/skills/llm-wiki/SKILL.md`
- `integrations/claude/skills/README.md`
- `integrations/claude/install/README.md`
- `integrations/claude/install/install.ps1`
- `integrations/claude/install/install.sh`
- `integrations/claude/README.md`
- `docs/claude-adapter-plan.md`
- `docs/capability-mapping.md`
- `docs/roadmap.md`
- `docs/roadmap-schedule.md`
- `tests/unit/test_r4_3_claude_adapter_assets.py`

Optional, only if kept as thin wrappers:

- `integrations/claude/commands/wiki.md`
- `integrations/claude/commands/save.md`

R4.3 should not create active hooks, active subagents, `.claude-plugin`, or Obsidian-specific assets.

## Command Mapping

The Claude local adapter MVP should preserve the R4.2 command mapping:

| Claude intent | Neutral command |
|---|---|
| `/wiki` on a new vault | `llm-wiki init <vault> --purpose "..."` |
| `/wiki` on an existing vault | `llm-wiki continue <vault>` |
| `/wiki transport` | `llm-wiki detect-transport <vault>` |
| `/wiki status` | `llm-wiki status <vault>` |
| `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |
| `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |
| `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |
| `/wiki search <query>` | `llm-wiki search <vault> "<query>"` |
| `/wiki query <question>` | `llm-wiki query <vault> "<question>"` |
| `/wiki lint` | `llm-wiki lint <vault>` |
| `/save` | `llm-wiki save <vault> --title "..." --content "..."` |

The adapter may describe these as Claude instructions. It must not reimplement neutral core operations in Markdown prompt text.

## Installation Policy

R4.3 should follow R4.1's conservative installer posture:

- installation is explicit;
- dry-run is available;
- destination override is available for tests;
- existing different destinations fail by default;
- replace requires an explicit flag;
- no global Claude user settings are edited automatically;
- no user-level `~/.claude` files are modified by default;
- Windows support uses native PowerShell;
- macOS and Linux support use POSIX shell;
- examples use symbolic home paths such as `$HOME` and `~`, not private absolute paths.

The default target should be project-local, not global:

- `CLAUDE.template.md` can be copied to `CLAUDE.md` or `.claude/CLAUDE.md`;
- the Claude skill can be copied under `.claude/skills/llm-wiki/`;
- optional command wrappers can be copied under `.claude/commands/`.

R4.3 should document that project-local installation is shareable with a repository, while local `.claude/settings.local.json` remains a user-specific file and should not be generated by default.

## Hooks And Subagents Boundary

R4.3 must not enable hooks or subagents by default.

Allowed R4.3 behavior:

- document why hooks and subagents are deferred;
- include non-installed examples in docs if clearly labeled as future work;
- add guard tests that no active `hooks.json`, `.claude/settings.json` hook configuration, `.claude/agents/`, or auto-commit hook asset is generated.

Disallowed R4.3 behavior:

- active `SessionStart`, `PostToolUse`, `Stop`, or `PostCompact` hooks;
- auto-commit behavior;
- automatic hot-cache reinjection;
- parallel ingest subagents;
- verifier subagents;
- filesystem writes outside explicit adapter installation destinations;
- default edits to user-global Claude settings.

## Testing Strategy

R4.3 should be test-first.

Minimum guard tests:

- Claude adapter assets exist and have no damaged text or private local paths.
- Claude skill frontmatter declares `name: llm-wiki` and a useful description.
- Claude skill maps `/wiki` and `/save` intents to neutral `llm-wiki` commands.
- `CLAUDE.template.md` states raw source immutability, artifact-level parity, and no byte-for-byte parity.
- Installer docs describe project-local install, dry-run, destination override, explicit replace, and no automatic global Claude settings mutation.
- PowerShell and POSIX installers support dry-run and fixture destinations without touching user-global files.
- Guard tests assert no active hooks, subagents, `.claude-plugin`, `autoresearch`, `canvas`, auto-commit behavior, DragonScale, or methodology modes are shipped in R4.3.
- Existing R4.2 parity docs remain true after R4.3 assets are added.

No live Claude Code, Obsidian, network, LLM, or user-global configuration should be required for tests.

## Compatibility

R4.3 targets local Claude Code use on Windows and macOS/Linux.

Windows support must not require WSL or Git Bash. PowerShell installation examples should be first-class.

macOS/Linux support should use POSIX shell.

Codex App and Codex CLI behavior must remain unchanged.

The neutral core must remain dependency-free unless a separate core design approves dependencies.

## Non-Goals

R4.3 must not implement:

- active Claude hooks;
- Claude subagents;
- `.claude-plugin` packaging;
- marketplace publishing;
- user-global Claude configuration mutation;
- `autoresearch`;
- canvas workflows;
- hybrid retrieval, vector search, reranking, or qmd integration;
- DragonScale memory;
- methodology modes;
- automatic Git commits;
- Obsidian-specific setup;
- remote Codex Web or remote Claude Web support;
- byte-for-byte prose parity;
- full `claude-obsidian` parity.

## Risks

### Risk: confusing command files and skills

Mitigation: pick Claude skills as the canonical surface and make any command files thin optional wrappers.

### Risk: overclaiming parity

Mitigation: continue artifact-level parity language and guard tests that reject full `claude-obsidian` parity claims.

### Risk: mutating user-global Claude configuration

Mitigation: project-local install by default, explicit dry-run, destination override, explicit replace, and no automatic writes to `~/.claude`.

### Risk: hooks cause unexpected side effects

Mitigation: R4.3 does not ship active hook configuration. Hooks remain future adapter work.

### Risk: duplicated core behavior in prompt assets

Mitigation: prompt assets should instruct Claude to call `llm-wiki` commands, not restate file-writing algorithms as an alternative implementation.

## Acceptance Criteria

R4.3 is ready for implementation planning when this design is accepted.

The future implementation is complete when:

- Claude local adapter MVP assets exist;
- `/wiki` and `/save` intent mapping is documented in Claude-facing assets;
- project-local install docs and scripts are explicit, dry-run capable, and fixture-testable;
- no active hooks, subagents, `.claude-plugin`, or advanced `claude-obsidian` features are shipped;
- public docs avoid private local paths and damaged text;
- R4.3 focused tests pass;
- adjacent R4.2 adapter parity tests pass;
- full test suite passes;
- `git diff --check` and range-based whitespace checks pass;
- `pyproject.toml` keeps `dependencies = []`.

