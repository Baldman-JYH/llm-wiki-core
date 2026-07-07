# Capability Mapping

This document maps LLM Wiki capabilities to neutral core, Codex adapter, Claude adapter, or deferred extension work.

| Capability | Layer | Current status | Codex adapter behavior | Claude adapter behavior | Boundary |
|---|---|---|---|---|---|
| Vault scaffold | Core + adapter | Complete | Map setup triggers to `llm-wiki init` | Map `/wiki` on a new vault to `llm-wiki init` | Adapter owns entry wording; core owns artifacts |
| Raw source preservation | Core | Complete | Remind Codex not to modify `.raw/` | Remind Claude not to modify `.raw/` | Raw source mutation is forbidden |
| Local file ingest | Core | Complete | Map source triggers to `llm-wiki ingest` | Map `/wiki ingest <source>` to `llm-wiki ingest` | Source must be under `.raw/` |
| Batch ingest | Core | R3.1 complete | Map folder triggers to `llm-wiki ingest-batch` | Map `/wiki ingest-batch <source-root>` to `llm-wiki ingest-batch` | Reuses core ingest behavior |
| URL ingest | Core | R3.2 complete | Map URL triggers to `llm-wiki ingest-url` | Map `/wiki ingest-url <url>` to `llm-wiki ingest-url` | One explicit URL; no crawling |
| Search durable wiki pages | Core | R3.3 complete | Map search triggers to `llm-wiki search` | Map `/wiki search <query>` to `llm-wiki search` | Read-only; no raw-source search by default |
| Query wiki | Core | Complete | Map question triggers to `llm-wiki query` | Map `/wiki query <question>` to `llm-wiki query` | Reads hot/index and ranked pages |
| Save durable insight | Core + adapter | Complete | Map save triggers to `llm-wiki save` | Map `/save` to `llm-wiki save` | Save durable knowledge, not chat noise |
| Lint wiki | Core | Complete | Map lint triggers to `llm-wiki lint` | Map `/wiki lint` to `llm-wiki lint` | Reports health and gaps |
| Adapter parity baseline | Docs + tests | R4.2 complete | Natural-language triggers map to neutral commands | Slash-command intent maps to neutral commands | Artifact-level parity; no byte-for-byte parity |
| Codex AGENTS template | Codex adapter | Complete | Provide repo-local bootstrap instructions | No Claude dependency | Adapter-only |
| Codex user-level skill | Codex adapter | R4.1 complete | Provide explicit user-level skill install helpers | No Claude dependency | Opt-in only; does not mutate global config automatically |
| Codex plugin package | Codex adapter | Deferred | Keep as future target | No Claude dependency | Not marketplace-ready through R4.2 |
| Claude advanced schema guidance | Claude adapter | Deferred | No Codex dependency | Advanced `CLAUDE.md` schema, hooks/subagents, and `.claude-plugin` reconstruction remain future work | Adapter-only; never neutral core |
| Claude local adapter MVP | Claude adapter | R4.3 complete | No Codex dependency | Project-local skill and thin `/wiki` `/save` wrappers | Adapter-only; no hooks or subagents |
| Claude advanced command surfaces | Claude adapter | Deferred | No Codex dependency | Hooks, subagents, `.claude-plugin`, autoresearch, canvas, hybrid retrieval, DragonScale, methodology modes, and related advanced command surfaces are deferred for future Claude reconstruction | Adapter-only; never neutral core |
| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Keep as future Claude-only reconstruction | Adapter-only; never neutral core |
| Autoresearch | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
| Canvas workflows | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
| Vector or hybrid retrieval | Deferred extension | Deferred | Do not claim support | Do not claim support | Future retrieval design |
| Knowledge organization foundation | Core | R5.0 complete | Expose `generic` as the default organization mode | Expose `generic` as the default organization mode | Foundation only; optional methodology modes remain deferred |
| Organization route adoption | Core | R5.1 complete | Use the same generic route contract for local Codex workflows | Use the same generic route contract for local Claude workflows | Foundation only; no non-generic modes |
| DragonScale or log-folding memory | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
| Methodology modes | Deferred extension | Deferred | Do not claim support | Do not claim support | Separate design required |
