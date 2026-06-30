# R3.2 URL Ingest Design

## Status

Approved for design by the user on 2026-06-30.

## Context

The canonical abstraction for this project is Karpathy's LLM Wiki gist:

- `raw/` stores source facts and materials.
- `wiki/` stores durable Markdown knowledge synthesized from those sources.
- `schema/` stores rules, prompts, and behavior constraints.

`claude-obsidian` remains a concrete Claude Code + Obsidian reference implementation of that abstraction. `llm-wiki-core` should generalize the same effect for Codex App, Codex CLI, and future local agents without depending on Claude-specific commands or hooks.

R3.1 completed local Markdown batch ingest. R3.2 adds URL ingest as a source acquisition path. URL ingest must not become a generic web downloader. It must bring an external source into the Raw Source layer, then reuse the existing ingest workflow to update Wiki artifacts.

## Goals

R3.2 should provide a narrow, testable URL ingest MVP:

1. Add a neutral `ingest-url` operation and CLI command.
2. Fetch one explicit `http` or `https` URL supplied by the user.
3. Save every fetch as an immutable Raw Source snapshot.
4. Preserve enough raw response data for later audit.
5. Generate a normalized Markdown source file that existing ingest can process.
6. Update `.raw/.manifest.json`, `wiki/sources/*`, `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
7. Record URL provenance in manifest without replacing Raw Source content.
8. Keep filesystem transport as the runtime write path.

## Non-Goals

R3.2 does not implement:

- full readability extraction;
- defuddle integration;
- JavaScript rendering;
- crawling more than the explicit URL;
- authenticated pages, cookies, browser session reuse, or forms;
- image, PDF, video, audio, or vision ingest;
- deep retrieval, BM25, vector search, reranking, or LLM synthesis;
- Obsidian CLI write support for URL acquisition.

## Recommended Approach

Use an immutable Snapshot Bundle.

Each `ingest-url` run creates a new Raw Source snapshot under `.raw/url/`. The snapshot contains:

- a raw response payload file;
- a normalized Markdown source file;
- optional sidecar metadata if useful for readability and tests.

The normalized Markdown source is the file passed into the existing ingest workflow. The raw response payload remains available for audit and later cleaner improvements.

This approach is preferred over saving only a Markdown file because it better preserves source fidelity. It is preferred over full web-cleaning integration because R3.2 should keep the MVP small and cross-platform.

## Snapshot Layout

The exact path may be refined during implementation, but the layout should preserve these semantics:

```text
.raw/
  url/
    <date>/
      <host-slug>/
        <timestamp>-<url-hash>/
          source.md
          response.html
          metadata.json
```

For non-HTML text responses, the raw payload may use `response.txt`. For unknown textual content, use a conservative extension such as `response.bin` only if the MVP deliberately accepts that content type. The normalized source for ingest is always `source.md`.

Snapshot paths are immutable. Re-ingesting the same URL creates a new snapshot unless implementation later adds an explicit dedupe mode. R3.2 must not overwrite an earlier URL snapshot.

## Normalized Source

`source.md` should be deterministic and human-readable. It should include source provenance near the top, then extracted or preserved text:

```markdown
---
source_type: url
source_url: "https://example.com/article"
fetched_at: 2026-06-30T00:00:00+08:00
http_status: 200
content_type: "text/html; charset=utf-8"
raw_snapshot_path: ".raw/url/2026-06-30/example-com/..."
---

# URL Source: Example Title

Original URL: https://example.com/article

## Extracted Text

...
```

HTML extraction should be minimal and deterministic:

- remove scripts and styles;
- decode HTML entities;
- keep readable text;
- avoid claiming full article readability;
- avoid introducing external runtime dependencies in R3.2.

If extraction cannot produce useful text, the operation should fail clearly before invoking the ingest workflow. It may preserve the raw payload and metadata snapshot for audit, but it must not create a misleading `source.md`, update Wiki pages, or write a successful manifest record.

## Manifest Extension

Existing manifest records currently use `source_type: "file"`. URL snapshots should keep the same top-level `sources` map and add URL provenance fields to the source record:

```json
{
  "source_path": ".raw/url/2026-06-30/example-com/.../source.md",
  "source_type": "url",
  "status": "ingested",
  "first_ingested": "2026-06-30T00:00:00+08:00",
  "last_ingested": "2026-06-30T00:00:00+08:00",
  "content_fingerprint": "sha256:...",
  "source_url": "https://example.com/article",
  "fetched_at": "2026-06-30T00:00:00+08:00",
  "http_status": 200,
  "content_type": "text/html; charset=utf-8",
  "raw_snapshot_path": ".raw/url/2026-06-30/example-com/.../response.html",
  "generated_pages": ["wiki/sources/Example Title.md"],
  "updated_pages": ["wiki/index.md", "wiki/log.md", "wiki/hot.md"],
  "notes": ""
}
```

Lint should continue accepting `source_type: "file"` and should also accept `source_type: "url"` once R3.2 is implemented.

## CLI Contract

Add:

```text
llm-wiki ingest-url <vault> <url> [--json]
```

Possible later flags, deferred unless implementation needs them:

- `--title`
- `--timeout`
- `--max-bytes`
- `--force`

R3.2 should choose conservative defaults for timeout and response size limit. If a flag is not necessary for the MVP, leave it out and keep behavior documented.

Text output should match existing CLI style:

```text
ingest-url success
url: https://example.com/article
snapshot: .raw/url/...
source: .raw/url/.../source.md
created: 2
updated: 4
next: Query the wiki, lint the vault, or ingest another URL.
```

JSON output should serialize the result dataclass as existing commands do.

## URL Safety Policy

R3.2 should accept only explicit `http` and `https` URLs.

It should reject:

- `file:`, `ftp:`, `data:`, `javascript:`, and other non-HTTP schemes;
- empty or malformed URLs;
- redirects to unsupported schemes.

The fetcher should use:

- a finite timeout;
- a maximum response size;
- no cookies;
- no credential prompts;
- no browser session;
- no JavaScript execution.

R3.2 will not block private-network or loopback URLs because local HTTP server tests and explicit local documentation workflows should remain possible. This is acceptable for the MVP because `ingest-url` only fetches a user-supplied URL from a local CLI/App context, uses no credentials, and does not reuse browser sessions. The limitation must be documented.

## Data Flow

1. User runs `llm-wiki ingest-url <vault> <url>`.
2. Core validates the URL.
3. Core fetches the response with conservative limits.
4. Core writes an immutable snapshot under `.raw/url/`.
5. Core creates `source.md` from URL metadata and readable text.
6. Core invokes the existing single-source ingest workflow on `source.md`.
7. Core updates the manifest record from `source_type: "file"` semantics to URL provenance semantics, or calls a shared ingest helper that can write the correct record directly.
8. Core returns a structured result with snapshot path, normalized source path, files changed, warnings, and next suggested action.

## Error Handling

The operation should fail without partial Wiki updates when:

- the URL is invalid;
- the scheme is unsupported;
- fetching times out;
- the response exceeds the configured size limit;
- the response content type is unsupported;
- the snapshot cannot be written;
- the normalized Markdown source cannot be created.

If a snapshot has been written but normalization or ingest fails, the operation should preserve the raw payload and metadata for audit, report the snapshot path and error, and avoid reporting the source as successfully ingested. Wiki artifacts and manifest records must only represent successful ingest results.

## Testing Strategy

R3.2 should add focused tests:

- unit tests for URL validation;
- unit tests for snapshot path generation;
- unit tests for HTML/text normalization;
- operation tests using a local test HTTP server;
- CLI tests for text output and `--json`;
- manifest tests proving `source_type: "url"` and URL provenance fields;
- immutability tests proving repeated URL ingest creates a new snapshot instead of overwriting;
- lint tests proving URL source records are accepted;
- regression tests showing existing `ingest` and `ingest-batch` behavior is unchanged.

Network tests should not depend on the public internet. Use a local HTTP server or a fake fetcher.

## Documentation Updates

R3.2 should update:

- README command list and examples;
- `docs/operation-contract.md`;
- `docs/manifest-schema.md`;
- `docs/roadmap-schedule.md`;
- any user guide section that explains ingest workflows.

Documentation must continue explaining that Karpathy's LLM Wiki gist is the canonical abstraction, while `claude-obsidian` is a concrete reference implementation.

## Acceptance Criteria

R3.2 is complete when:

1. `llm-wiki ingest-url` can ingest one explicit local-test HTTP URL.
2. Each run creates a new immutable raw snapshot.
3. The original response payload is preserved.
4. A normalized Markdown source is generated under `.raw/url/`.
5. Existing Wiki artifacts are updated through the ingest workflow.
6. Manifest records URL provenance.
7. Lint passes on a vault containing URL-ingested sources.
8. Full tests pass on Windows without WSL or Git Bash.
9. No required runtime dependency is added unless explicitly justified.

## Open Implementation Choice

The implementation may either:

1. call `ingest_source(...)` and then adjust the manifest record to URL provenance; or
2. refactor the ingest internals so file and URL sources share one manifest-writing helper.

Option 2 is cleaner if it stays small. Option 1 is acceptable if it avoids broad churn and is covered by tests.
