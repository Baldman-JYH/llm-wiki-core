# Manifest Schema

This document defines the public schema for `.raw/.manifest.json`. The manifest records durable source state and provenance without replacing raw source content.

## Location

```text
.raw/.manifest.json
```

## Design Principles

- the manifest belongs to the neutral core
- it must stay adapter-agnostic and JSON-based
- it tracks source state, provenance, and affected wiki pages
- it does not replace `.raw/` source payloads
- it does not replace `wiki/log.md` or `wiki/index.md`

## Top-Level Shape

```json
{
  "schema_version": 1,
  "updated": "2026-06-30T00:00:00+08:00",
  "sources": {
    "articles/example.md": {
      "source_path": ".raw/articles/example.md",
      "source_type": "file",
      "status": "ingested",
      "first_ingested": "2026-06-30T00:00:00+08:00",
      "last_ingested": "2026-06-30T00:00:00+08:00",
      "content_fingerprint": "sha256:...",
      "generated_pages": [
        "wiki/sources/Example.md"
      ],
      "updated_pages": [
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md"
      ],
      "notes": ""
    }
  }
}
```

## Source Types

`source_type` currently supports two values:

- `file` for local Markdown sources already stored under `.raw/`
- `url` for immutable URL ingest snapshots stored under `.raw/url/`

## Shared Source Record Fields

| Field | Type | Description |
|---|---|---|
| `source_path` | string | Vault-relative source path. Must remain under `.raw/`. |
| `source_type` | string | `file` or `url`. |
| `status` | string | `ingested`, `skipped`, or `failed`. |
| `first_ingested` | string | First successful ingest timestamp in ISO 8601 form. |
| `last_ingested` | string | Most recent ingest timestamp in ISO 8601 form. |
| `content_fingerprint` | string | Content fingerprint such as `sha256:<hex>`. |
| `generated_pages` | array | Pages first created from this source. |
| `updated_pages` | array | Pages updated during the latest ingest. |
| `notes` | string | Optional operator-facing note. |

## URL Source Provenance Fields

When `source_type` is `url`, the source record may include:

| Field | Type | Description |
|---|---|---|
| `source_url` | string | Canonical source URL used for user-facing provenance. |
| `requested_url` | string | Original user-supplied URL before redirects, if tracked separately. |
| `fetched_at` | string | Fetch timestamp in ISO 8601 form. |
| `http_status` | number | Final HTTP status code. |
| `content_type` | string | Response content type captured at fetch time. |
| `raw_snapshot_path` | string | Vault-relative path to the decoded raw snapshot payload under `.raw/url/`. |

Example URL source record:

```json
{
  "source_path": ".raw/url/2026-06-30/example-com/2026-06-30T01-02-03Z-abc123/source.md",
  "source_type": "url",
  "status": "ingested",
  "first_ingested": "2026-06-30T01:02:03+08:00",
  "last_ingested": "2026-06-30T01:02:03+08:00",
  "content_fingerprint": "sha256:...",
  "source_url": "https://example.com/article",
  "requested_url": "https://example.com/article",
  "fetched_at": "2026-06-30T01:02:03+08:00",
  "http_status": 200,
  "content_type": "text/html; charset=utf-8",
  "raw_snapshot_path": ".raw/url/2026-06-30/example-com/2026-06-30T01-02-03Z-abc123/response.html",
  "generated_pages": [
    "wiki/sources/Example Article.md"
  ],
  "updated_pages": [
    "wiki/index.md",
    "wiki/log.md",
    "wiki/hot.md"
  ],
  "notes": ""
}
```

## Source Key

The `sources` object key should remain a stable vault-relative identifier for the raw source record, typically the path below `.raw/`.

## Validation Rules

Lint should verify:

- manifest JSON is valid
- `schema_version` is `1`
- `sources` is an object
- each source record is an object
- each `source_path` stays under `.raw/`
- each `source_type` is `file` or `url`
- `content_fingerprint` is non-empty

## Current Boundary

R3.2 URL ingest is text-only. Binary or non-decodable responses are rejected instead of being represented as valid URL source records.
