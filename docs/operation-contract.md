# Operation Contract

This document defines the stable public contract for core `llm-wiki-core` operations: purpose, inputs, outputs, error modes, and validation boundaries. Adapters may expose these operations through commands, skills, or UI, but they should not change the underlying semantics.

## Operation List

- `init`
- `status`
- `continue`
- `ingest`
- `ingest-url`
- `query`
- `lint`
- `save`
- `detect-transport`

## Shared Rules

- Raw source material is preserved in `.raw/`.
- Wiki artifacts are stored with vault-relative paths.
- `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md` keep their durable coordination roles.
- `.raw/.manifest.json` records source state and provenance.
- Artifact-level equivalence matters more than byte-for-byte identical prose.

## `init`

### Purpose

Initialize a local LLM Wiki vault scaffold.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `purpose` | One-sentence user purpose for the vault. |

### Output

- `.raw/` and `.raw/.manifest.json`
- `wiki/` scaffold and required pages
- adapter entry file such as `AGENTS.md`

### Error Modes

- refuse to overwrite conflicting non-wiki content
- fail clearly if scaffold files cannot be created

### Validation

- required folders and pages exist
- manifest is valid JSON

## `status`

### Purpose

Report whether the vault is initialized and what state it is in.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |

### Output

- initialization status
- source count
- transport status
- missing required paths
- next suggested action

### Error Modes

- not a vault
- partially initialized vault

### Validation

- no wiki mutation by default

## `continue`

### Purpose

Recover recent wiki context from durable artifacts instead of chat history.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |

### Output

- hot context summary
- index context
- recent log entries
- next suggested action

### Error Modes

- missing `hot` or `index` files

### Validation

- no wiki mutation by default

## `ingest`

### Purpose

Ingest one local Markdown source that already lives under `.raw/`.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `source_path` | Vault-relative path under `.raw/`. |
| `force` | Re-ingest even if the fingerprint is unchanged. |

### Output

- updated `.raw/.manifest.json`
- created or updated wiki pages
- updated `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`

### Error Modes

- source missing
- source outside `.raw/`
- source unreadable

### Validation

- raw input remains unchanged
- manifest source record is valid

## `ingest-url`

### Purpose

Fetch one explicit `http` or `https` URL, preserve an immutable `.raw/url/` snapshot, create a normalized Markdown source, and then reuse the existing ingest flow to update wiki artifacts.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `url` | One explicit `http` or `https` URL supplied by the user. |
| `transport` | Optional runtime transport override. Filesystem remains the default portable write path. |

### Output

- immutable snapshot files under `.raw/url/`
- decoded raw response text for audit
- response metadata and provenance
- normalized Markdown `source.md`
- updated manifest and wiki artifacts through the ingest workflow

### Error Modes

| Error | Handling |
|---|---|
| invalid or unsupported scheme | reject before fetch |
| timeout or response too large | fail without wiki updates |
| binary or non-decodable response | reject because R3.2 is text-only |
| snapshot write or normalization failure | preserve the audit boundary and report failure |

### Validation

- only explicit `http` and `https` URLs are accepted
- URL snapshots are immutable
- URL manifest records use `source_type: "url"`
- lint accepts `file` and `url`
- full readability, defuddle, JavaScript rendering, authenticated pages, and crawling remain out of scope

## `query`

### Purpose

Answer a question from the current wiki state.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `question` | User question. |

### Output

- answer grounded in wiki pages
- cited wiki paths
- explicit gaps or uncertainty

### Error Modes

- vault not initialized
- not enough wiki evidence

### Validation

- no wiki mutation unless the user explicitly chooses to save

## `lint`

### Purpose

Check wiki health and write a stable lint report.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `write_report` | Whether to write a lint report under `wiki/meta/`. |

### Output

- required path checks
- manifest JSON checks
- manifest source type checks
- frontmatter checks
- dead wikilink checks
- orphan-page checks
- optional report path

### Error Modes

- invalid manifest JSON
- unsupported manifest source types
- malformed frontmatter

### Validation

- report format stays stable
- lint does not auto-fix content unless explicitly requested by the user

## `save`

### Purpose

Persist durable insight back into the wiki.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `content` | Durable insight content. |
| `title` | Optional page title. |

### Output

- created or updated wiki page
- updated `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`

### Error Modes

- content lacks durable value
- title conflict

### Validation

- frontmatter remains valid

## `detect-transport`

### Purpose

Detect runtime transport capability metadata for the current vault.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `force` | Refresh snapshot even if one exists. |

### Output

- transport snapshot metadata
- optional verification notes

### Error Modes

- optional transport unavailable
- snapshot write failure

### Validation

- filesystem is always available
- the official `obsidian` CLI remains optional and verified-only

## Operation Result Shape

Operations should report:

- operation name
- status
- created files
- updated files
- warnings
- next suggested action
