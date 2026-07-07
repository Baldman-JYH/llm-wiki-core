# ADR 0008: Optional Organization Modes

Status: accepted

## Context

The MVP intentionally supports only `generic` organization mode. This keeps the first-use workflow focused on the LLM Wiki loop: raw sources remain durable, the agent maintains Markdown wiki artifacts, and index/log/hot preserve continuity across sessions.

The roadmap now includes methodology modes such as LYT, PARA, and Zettelkasten. These methods can be useful, but they are not the canonical abstraction. The canonical abstraction remains Karpathy's LLM Wiki pattern. `AgriciDaniel/claude-obsidian` is a reference implementation case that proves useful workflows, not a requirement to copy every method into the neutral core.

## Decision

Organization modes are optional extensions.

`generic` remains the default organization mode for `init` and for adapter guidance.

R5.0 will introduce a neutral organization definition boundary before adding any non-generic methodology runtime. The boundary may describe scaffold directories, seed pages, page type routes, lint expectations, and adapter notes.

LYT, PARA, Zettelkasten, DragonScale, semantic stale-claim lint, and comparison workflow helpers require separate implementation plans before they can be claimed as supported.

## Consequences

- First-use setup remains simple and methodology-neutral.
- The neutral core can grow without becoming coupled to one personal knowledge management method.
- Codex and Claude adapters can expose the same organization contract without changing artifact semantics.
- Future mode implementations must preserve raw source immutability, durable Markdown wiki artifacts, index/log/hot continuity, and artifact-level equivalence.
- Documentation must distinguish foundation support from completed optional mode support.
