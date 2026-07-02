# R4.2 Adapter Parity Baseline And Claude Reconstruction Design

Date: 2026-07-02

## Summary

R4.2 should define the first reliable parity baseline between the neutral `llm-wiki-core` project, the existing Codex adapter, and a future Claude Code adapter reconstructed from the `AgriciDaniel/claude-obsidian` reference implementation.

The goal is not to copy `claude-obsidian` wholesale. The goal is to preserve the Karpathy LLM Wiki pattern as the canonical abstraction, treat `claude-obsidian` as one proven implementation case, and define how Codex App / Codex CLI and Claude Code can drive the same durable Markdown Wiki artifacts through a shared core.

R4.2 is a design and guardrail milestone. It should produce a documented parity contract and tests that keep the project honest before any Claude-specific commands, hooks, subagents, or plugin assets are generated.

## Source Of Truth

The canonical idea source is Karpathy's LLM Wiki gist:

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

The pattern says:

- humans curate sources and direct exploration;
- raw sources are immutable source-of-truth inputs;
- the LLM maintains a durable, interlinked Markdown wiki;
- a schema file such as `AGENTS.md` or `CLAUDE.md` disciplines the agent;
- ingest, query, save, lint, index, and log operations make knowledge compound over time.

`AgriciDaniel/claude-obsidian` is the reference implementation case for Claude Code + Obsidian:

https://github.com/AgriciDaniel/claude-obsidian

It is not the canonical abstraction and should not define the neutral core by itself. Its value is evidence: it shows which workflows are useful in practice, which parts are Claude-only adapter mechanics, and which advanced features should stay outside the MVP parity baseline until explicitly designed.

## Why R4.2 Comes Next

R4.1 completed explicit user-level Codex skill installation for local Codex App and Codex CLI. The remaining user goal is broader: Codex and Claude should be able to achieve the same LLM Wiki effect with the same command intent and compatible artifacts.

Directly implementing a Claude adapter now would be premature because `claude-obsidian` includes several layers at once:

- core LLM Wiki operations;
- Claude Code slash commands;
- Claude hooks;
- Claude subagents;
- Obsidian-specific automation;
- retrieval, canvas, autoresearch, and methodology extensions.

R4.2 should separate those layers before implementation. This keeps the neutral core small, portable, and aligned with the Karpathy pattern.

## Parity Definition

R4.2 should use artifact-level parity, not byte-for-byte parity.

Byte-for-byte parity is the wrong target for LLM-maintained wikis because prose ordering, wording, and synthesis style may vary across agents and models. It would create fragile tests and reward mechanical imitation over useful knowledge maintenance.

Artifact-level parity is the right target for this project. Codex and Claude should produce compatible durable outcomes:

- the same vault structure;
- the same raw-source immutability rule;
- the same page categories;
- compatible frontmatter and wikilinks;
- updated `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`;
- equivalent operation logs;
- equivalent lint and health checks;
- equivalent command intent mapping;
- no false claim that advanced `claude-obsidian` behavior is already implemented.

## Layer Model

R4.2 should document and test four layers.

### Neutral Core

The neutral core owns durable wiki artifacts and portable operations:

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

The core owns file formats, frontmatter policy, wikilink policy, raw manifest behavior, transport contracts, index maintenance, log maintenance, and hot context maintenance.

The core must not know about Codex skills, Claude slash commands, Claude hooks, Claude subagents, Obsidian plugins, or marketplace packaging.

### Codex Adapter

The Codex adapter owns local Codex App / Codex CLI usage:

- `integrations/codex/skills/llm-wiki/SKILL.md`
- Codex natural-language trigger mapping;
- `AGENTS.md` template behavior;
- repo-local install guidance;
- explicit user-level skill installation;
- future optional Codex plugin packaging.

The Codex adapter maps user intent to neutral core commands. It must not reimplement core behavior.

### Claude Adapter

The future Claude adapter should own Claude Code-specific behavior:

- `CLAUDE.md` or equivalent Claude schema entry;
- slash commands such as `/wiki` and `/save`;
- Claude Code hook configuration;
- Claude Code subagent descriptions;
- Claude-specific plugin or local installation structure if needed.

The Claude adapter should map Claude-specific surfaces to the same neutral core commands already used by the Codex adapter.

### Deferred Extensions

The following `claude-obsidian` capabilities should remain deferred until they receive their own designs:

- `autoresearch`;
- canvas workflows;
- hybrid retrieval and reranking;
- DragonScale or log-folding memory;
- methodology modes such as LYT, PARA, and Zettelkasten;
- multi-agent batch orchestration;
- Obsidian-specific dashboards, bases, plugins, or advanced templates;
- automatic commits or session hooks that mutate Git state.

These features are valuable, but they are not required to prove the first Codex / Claude parity baseline.

## Command Intent Mapping

R4.2 should define a shared command-intent table. The same intent can be expressed as Codex natural language, Claude slash commands, or direct CLI calls.

| Intent | Codex surface | Claude surface | Neutral command |
|---|---|---|---|
| Set up a wiki | `set up wiki` | `/wiki` | `llm-wiki init <vault> --purpose "..."` |
| Check transport | `check transport` | `/wiki transport` | `llm-wiki detect-transport <vault>` |
| Check status | `check wiki status` | `/wiki status` | `llm-wiki status <vault>` |
| Continue context | `continue wiki` | `/wiki` on existing vault | `llm-wiki continue <vault>` |
| Ingest one source | `ingest this source` | `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |
| Ingest a folder | `ingest this folder` | `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |
| Ingest a URL | `ingest this URL` | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |
| Search pages | `search wiki for X` | `/wiki search X` | `llm-wiki search <vault> "X"` |
| Ask a question | `what does the wiki know about X` | `/wiki query X` | `llm-wiki query <vault> "X"` |
| Save insight | `save this insight` | `/save` | `llm-wiki save <vault> --title "..." --content "..."` |
| Lint health | `lint the wiki` | `/wiki lint` | `llm-wiki lint <vault>` |

This table is the baseline for future adapter implementation.

## User Experience

A local Codex user should keep using Codex App or Codex CLI with the existing `llm-wiki` skill and core CLI commands.

A future Claude Code user should be able to use familiar `claude-obsidian`-style entry points, but those entry points should be wrappers around `llm-wiki-core` behavior where possible.

The visible user outcome should be the same:

- the user supplies sources and questions;
- the agent updates a durable wiki;
- the raw layer stays immutable;
- the wiki layer is maintained by the agent;
- schema instructions make the agent disciplined;
- index, log, hot context, links, and lint reports preserve continuity.

## Documentation Scope

R4.2 should add or update:

- a public adapter parity baseline document;
- the Claude integration README;
- the capability mapping document;
- the roadmap and roadmap schedule;
- optional cross-links from Codex adapter docs where useful.

The docs should say that `llm-wiki-core` aims for portable artifact-level parity. They must not say that the project has full `claude-obsidian` feature parity.

## Test Strategy

R4.2 should add guard tests rather than runtime Claude integration tests.

Minimum tests:

- parity docs identify Karpathy's gist as the canonical abstract pattern;
- parity docs identify `AgriciDaniel/claude-obsidian` as a reference implementation case;
- parity docs define artifact-level parity and reject byte-for-byte parity;
- Codex and Claude surfaces map to the same neutral core commands for MVP operations;
- advanced `claude-obsidian` features remain deferred;
- Claude hooks and subagents are documented as adapter-only, never neutral core;
- public docs do not contain private local paths;
- docs do not claim full `claude-obsidian` parity.

No live Claude Code, Obsidian, or Codex App process should be required for R4.2 tests.

## File Scope

Expected implementation files for the next plan:

- `docs/adapter-parity-baseline.md`
- `docs/capability-mapping.md`
- `docs/roadmap.md`
- `docs/roadmap-schedule.md`
- `integrations/claude/README.md`
- `tests/unit/test_r4_2_adapter_parity_baseline_docs.py`
- optional focused tests if existing docs tests need to stay smaller

Neutral core operation code should not be touched in R4.2 unless a doc test exposes an existing naming inconsistency that can be fixed without changing behavior.

## Non-Goals

R4.2 must not implement:

- `.claude-plugin` generation;
- Claude Code hooks;
- Claude Code subagents;
- marketplace-grade Codex plugin packaging;
- `autoresearch`;
- canvas generation;
- hybrid retrieval, vector search, reranking, or qmd integration;
- methodology modes;
- DragonScale memory;
- automatic Git commits;
- remote Codex Web support;
- byte-for-byte golden-output parity.

## Risks

### Risk: overclaiming parity

Mitigation: use explicit artifact-level parity language and tests that reject full `claude-obsidian` parity claims.

### Risk: leaking adapter behavior into core

Mitigation: keep Claude commands, hooks, and subagents in `integrations/claude`; keep Codex skill packaging in `integrations/codex`; test that neutral core docs describe operations rather than adapter mechanics.

### Risk: underusing the `claude-obsidian` reference

Mitigation: classify the reference implementation capability by capability, preserving proven workflows as future adapter or extension targets instead of ignoring them.

### Risk: designing too much at once

Mitigation: R4.2 only creates the parity baseline and guard tests. It does not implement advanced adapter behavior.

## Acceptance Criteria

R4.2 is complete when:

- a public adapter parity baseline document exists;
- `integrations/claude/README.md` explains the reconstruction boundary;
- capability mapping distinguishes neutral core, Codex adapter, Claude adapter, and deferred extensions;
- Codex and Claude command intent mappings share the same neutral core operations;
- docs clearly state artifact-level parity, not byte-for-byte parity;
- docs do not claim full `claude-obsidian` parity;
- advanced `claude-obsidian` features remain deferred;
- focused R4.2 doc tests pass;
- the full test suite passes;
- `git diff --check` passes.

