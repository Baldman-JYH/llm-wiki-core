# Codex Command Contract

This document defines Codex App / Codex CLI adapter command semantics.
Natural-language triggers and target slash commands should map to the same
core operations.
Natural-language triggers are required; slash commands are a target UX layer.

## Entry Strategy

MVP uses two entry layers:

1. Natural-language triggers must work.
2. Slash commands are a target UX used to align the core workflow with the
   Claude Code + Obsidian reference experience from
   `AgriciDaniel/claude-obsidian`.

If Codex App and Codex CLI differ in slash-command support, natural language
plus skills must still complete the equivalent core work.

## Design Principles

- Command semantics align with the core `claude-obsidian` experience.
- Command entry points belong to the Codex adapter, not the neutral core.
- Core defines operation contracts; adapters map user triggers.
- Natural-language entry is not a second-class path.
- Slash commands are a convenient UX layer, not the only entry point.

## Command Mapping

| User intent | Natural-language examples | Target slash command | Core operation |
|---|---|---|---|
| Initialize or resume Wiki | `set up wiki`, `scaffold vault`, `continue wiki` | `/wiki` | `init` / `status` / `continue` |
| Ingest local raw source | `ingest .raw/articles/a.md`, `process this source` | `/wiki ingest <source>` | `ingest` |
| Ingest local raw folder | `ingest this folder`, `ingest .raw/articles` | `/wiki ingest-batch <source-root>` | `ingest-batch` |
| Ingest one URL | `ingest this URL`, `ingest https://example.com/article` | `/wiki ingest-url <url>` | `ingest-url` |
| Query Wiki | `what do you know about X`, `query: X` | `/wiki query <question>` | `query` |
| Search Wiki | `search wiki for X`, `find wiki pages about X` | `/wiki search <query>` | `search` |
| Lint Wiki | `lint the wiki`, `health check` | `/wiki lint` | `lint` |
| Save durable insight | `save this conversation`, `file this insight` | `/wiki save [title]` | `save` |
| Detect transport | `check wiki transport` | `/wiki transport` | `detect-transport` |

## `/wiki` Semantics

When the vault is not initialized:

1. Check whether the current directory already contains `.raw/` and `wiki/`.
2. Ask for the vault purpose.
3. Use the generic mode scaffold to create the base structure.
4. Create or update the project instruction file.
5. Create `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, and `wiki/overview.md`.
6. Create `.raw/.manifest.json`.
7. Run `detect-transport`.
8. Suggest the next action, such as adding a raw source and running `ingest`.

When the vault is initialized:

1. Read `wiki/hot.md`.
2. Read `wiki/index.md`.
3. Check recent `wiki/log.md` entries.
4. Report current status.
5. Suggest the next action: `ingest`, `search`, `query`, `lint`, or `save`.

## `ingest` Semantics

Ingest one local Markdown source under `.raw/`.

Natural-language examples:

```text
ingest .raw/articles/example.md
process this source
add this to the wiki
```

Target slash command:

```text
/wiki ingest .raw/articles/example.md
```

Behavior:

1. Confirm the target is under `.raw/`.
2. Read the raw source but do not modify it.
3. Check `.raw/.manifest.json`.
4. If the source was already ingested and the fingerprint is unchanged, ask whether to skip or force re-ingest.
5. Create or update the source summary.
6. Create or update entity / concept pages as needed.
7. Update `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
8. Update manifest.

## `ingest-batch` Semantics

Ingest a local Markdown folder or root under `.raw/`.

Natural-language examples:

```text
ingest this folder
ingest .raw/articles
```

Target slash command:

```text
/wiki ingest-batch .raw/articles
```

Behavior:

1. Confirm the target root is under `.raw/`.
2. Enumerate local Markdown sources only.
3. Read each raw source without modifying it.
4. Check `.raw/.manifest.json` before writing results.
5. Skip unchanged sources unless the user requests force re-ingest.
6. Create or update per-source wiki artifacts.
7. Update manifest, `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
8. Record per-source success, skipped, and failed outcomes in batch logs or summaries.

## `ingest-url` Semantics

Ingest one explicit URL.

Natural-language examples:

```text
ingest this URL
ingest https://example.com/article
```

Target slash command:

```text
/wiki ingest-url https://example.com/article
```

Behavior:

1. Accept one explicit URL per invocation.
2. Fetch the source as a text-oriented URL ingest flow.
3. Write an immutable snapshot under `.raw/url/` before deriving wiki artifacts.
4. Check `.raw/.manifest.json` and record the raw snapshot metadata.
5. Create or update the corresponding wiki artifacts from the preserved snapshot.
6. Update manifest, `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
7. No crawling, readability pipeline, JavaScript rendering, or authenticated fetch flow is included.

## `query` Semantics

Natural-language examples:

```text
what do you know about X?
query: X
based on the wiki, explain X
```

Target slash command:

```text
/wiki query <question>
```

Behavior:

1. Read `wiki/hot.md`.
2. Read `wiki/index.md`.
3. Select only the necessary relevant pages.
4. Synthesize an answer from selected wiki pages.
5. Cite wiki pages in the answer.
6. If the question exposes a knowledge gap, explicitly call it a gap.
7. If the answer has durable value, suggest saving it to `wiki/questions/`.

## `search` Semantics

Search is read-only and returns ranked durable wiki pages before query synthesis.

Natural-language examples:

```text
search wiki for X
find wiki pages about X
search wiki for durable knowledge
```

Target slash command:

```text
/wiki search <query>
```

Behavior:

1. Read durable wiki pages only.
2. Rank results with dependency-free BM25-style lexical retrieval.
3. Return page paths, titles, snippets, matched terms, and scores.
4. Keep `.raw/` out of the default search scope.
5. Return ranked wiki pages before query synthesis.
6. Search does not mutate wiki content.

## `lint` Semantics

Natural-language examples:

```text
lint the wiki
health check
find wiki gaps
```

Target slash command:

```text
/wiki lint
```

Behavior:

1. Check frontmatter.
2. Check dead wikilinks.
3. Check orphan pages.
4. Check index coverage for major pages.
5. Check whether log has recent operations.
6. Check whether hot cache is stale or too long.
7. Check whether manifest is parseable.
8. Output or write a lint report.

## `save` Semantics

Natural-language examples:

```text
save this conversation
file this insight
save as "Topic"
```

Target slash command:

```text
/wiki save [title]
```

Behavior:

1. Decide whether the current content has durable knowledge value.
2. Choose whether to save as a question, concept, source note, or session note.
3. Create or update the corresponding wiki page.
4. Update `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.

## `detect-transport` Semantics

Natural-language examples:

```text
check wiki transport
which transport is active?
```

Target slash command:

```text
/wiki transport
```

Behavior:

1. Detect filesystem transport.
2. Detect Obsidian CLI transport.
3. Write a transport snapshot.
4. Set preferred transport when verified; keep filesystem fallback available.
5. Report the active available transport.

## Codex App / CLI Differences

The MVP does not assume Codex App and Codex CLI have identical slash-command
support. Every target slash command must have an equivalent natural-language
trigger.

## Adapter Responsibilities

Codex adapter is responsible for:

- Providing the `AGENTS.md` template.
- Exposing skills or plugin metadata.
- Mapping natural-language triggers and slash commands.
- Guiding users in Codex App / Codex CLI.
- Calling core operations.

Core is not responsible for:

- Codex UI behavior.
- Codex App / CLI command registration details.
- Claude Code command compatibility.

## Non-Goals

- This contract does not implement `/autoresearch`.
- This contract does not implement `/canvas`.
- This contract does not implement hybrid retrieval commands.
- Slash command support is not the only entry path.
