# Milestone 5 Query And Save Design

## Goal

Implement a deterministic MVP for querying the Wiki and saving valuable content back into the Wiki.

## Confirmed Approach

Use Python core APIs plus CLI subcommands:

- Core API: `query_wiki(vault_root, question, depth="standard")`
- CLI: `llm-wiki query <vault> <question>`
- Core API: `save_insight(vault_root, content, title=None, target_type="question")`
- CLI: `llm-wiki save <vault> --content "..." [--title "..."] [--target-type question|concept]`

## Query Scope

The MVP query:

- reads `wiki/hot.md`
- reads `wiki/index.md`
- searches Markdown pages under `wiki/`
- returns a concise answer with wikilink citations
- reports gaps when no relevant pages are found
- does not modify the Wiki

This is not a semantic retrieval engine and does not call an LLM.

## Save Scope

The MVP save:

- creates or updates a Markdown page under `wiki/questions/` or `wiki/concepts/`
- writes required frontmatter
- updates `wiki/index.md`
- prepends to `wiki/log.md`
- overwrites `wiki/hot.md` as recent context

## Boundaries

- Do not implement deep query.
- Do not implement hybrid retrieval, BM25, embeddings, or rerank.
- Do not call an LLM.
- Do not auto-save query answers.
- Do not modify Raw Source.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Verification

Tests should validate:

- query returns cited Wiki pages when relevant pages exist
- query reports a gap when no relevant page exists
- query does not create or update Wiki files
- save creates a question page and updates index/log/hot
- save can create a concept page
- CLI query and CLI save print concise summaries
