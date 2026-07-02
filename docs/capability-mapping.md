# Capability Mapping

This document maps LLM Wiki capabilities to neutral core, Codex adapter, Claude adapter, or deferred work.

| Capability | Layer | Current status | Codex adapter behavior | Boundary |
|---|---|---|---|---|
| Vault scaffold | Core + adapter | Complete | Map setup triggers to `llm-wiki init` | Adapter owns entry wording; core owns artifacts |
| Raw source preservation | Core | Complete | Remind Codex not to modify `.raw/` | Raw source mutation is forbidden |
| Local file ingest | Core | Complete | Map source triggers to `llm-wiki ingest` | Source must be under `.raw/` |
| Batch ingest | Core | R3.1 complete | Map folder triggers to `llm-wiki ingest-batch` | Reuses core ingest behavior |
| URL ingest | Core | R3.2 complete | Map URL triggers to `llm-wiki ingest-url` | One explicit URL; no crawling |
| Search durable wiki pages | Core | R3.3 complete | Map search triggers to `llm-wiki search` | Read-only; no raw-source search by default |
| Query wiki | Core | Complete | Map question triggers to `llm-wiki query` | Reads hot/index and ranked pages |
| Save durable insight | Core + adapter | Complete | Map save triggers to `llm-wiki save` | Save durable knowledge, not chat noise |
| Lint wiki | Core | Complete | Map lint triggers to `llm-wiki lint` | Reports health and gaps |
| Codex AGENTS template | Codex adapter | Complete | Provide repo-local bootstrap instructions | Adapter-only |
| Codex user-level skill | Codex adapter | R4.0 readiness | Provide reusable skill docs | Does not mutate global config automatically |
| Codex plugin package | Codex adapter | Deferred | Keep as future target | Not marketplace-ready in R4.0 |
| Claude hooks and subagents | Claude adapter | Deferred | Do not generate from Codex adapter | Adapter-only; never neutral core |
| Vector or hybrid retrieval | Deferred | Deferred | Do not claim support | Future retrieval design |
