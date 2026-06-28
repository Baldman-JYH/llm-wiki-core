# Transport Contract

Transport is the boundary used by the agent to read and write Wiki artifacts.

## MVP Transport Order

The MVP transport order is:

1. Filesystem transport, the only implemented runtime transport in the MVP.
2. Obsidian CLI transport, which may be detected and recorded but does not become runtime eligible until its contract and capability verification pass.
3. MCP and REST API transports, deferred to later milestones.

## Filesystem Transport

Filesystem transport is the minimum viable transport.

From Milestone 9 onward, filesystem transport provides the minimum executable API:

| Method | Description |
|---|---|
| `read_text(relative_path)` | Read UTF-8 text. |
| `write_text(relative_path, content)` | Create or overwrite UTF-8 text and create parent directories as needed. |
| `append_text(relative_path, content)` | Append UTF-8 text and create parent directories as needed. |
| `exists(relative_path)` | Check whether a vault-relative path exists. |
| `list_markdown(root="wiki")` | List Markdown files in stable order. |
| `search_text(query, root="wiki")` | Run deterministic case-insensitive substring search over Markdown files. |

Filesystem transport does not require Obsidian, MCP, REST API, WSL, or Git Bash.
All public methods accept vault-relative paths and reject absolute paths, `..` traversal, or any path that resolves outside the vault.
`search_text` is transport-level local text search, not hybrid retrieval, BM25, vector search, or LLM synthesis.

## Obsidian CLI Transport

Obsidian CLI transport is an optional desktop-oriented transport path.

When an Obsidian CLI is present locally, the system may record availability metadata so the boundary is preserved for later runtime use. Until actual transport behavior is verified, filesystem remains the safe runtime path.

The intended transport surface includes:

- read
- write
- append
- list
- search
- backlinks
- daily note

If Obsidian CLI is missing or fails verification, the selector must return to filesystem transport.

From Milestone 16 onward, transport snapshots separate detection from implementation:

- `available: true` means an Obsidian CLI executable was detected.
- `implemented: false` means the core still lacks verified transport behavior.
- `preferred: filesystem` means current operations safely use filesystem transport.

## R2 Official Obsidian CLI Runtime Eligibility

R2 distinguishes the official `obsidian` CLI from the legacy `obsidian-cli` command.

The official `obsidian` CLI can become runtime eligible only after detection verifies vault binding and read/write/append/list/search capability probe results.

The legacy `obsidian-cli` command is recorded as legacy metadata and remains unimplemented in R2.

If the official CLI is missing, disabled, bound to the wrong vault, missing a capability, or returns a probe error, the runtime selector uses filesystem fallback.

## Transport Snapshot

The system should maintain a transport snapshot to record currently detected transports.

Suggested fields:

- schema version
- detected at
- platform
- vault root
- preferred
- fallback chain
- available transports
- per-transport implemented state
- per-transport reason
- manual override

## Runtime Transport Selection

Transport detection records machine state. Runtime selection decides which transport an operation actually uses.

From Milestone 17 onward, default runtime selection follows these rules:

- the snapshot is advisory metadata;
- only transports with `available: true` and verified runtime eligibility may be selected;
- the current MVP implemented runtime transport is filesystem;
- if no snapshot exists, or a snapshot points to a non-eligible transport, operations fall back to filesystem;
- `status` and `continue` preserve fallback warning details so users can understand why a preferred transport was not selected.

The current runtime selector is used by:

- `query`
- `lint`
- `status`
- `continue`
- `ingest`
- `save`

`init` still creates the vault scaffold directly and does not move to an Obsidian CLI write path before that transport is verified.

## Cross-Platform Requirements

- Core detection logic should be implemented in Python.
- Windows entry points use PowerShell.
- macOS and Linux entry points use shell scripts.
- Path handling must support Windows paths, spaces, and non-ASCII characters.

## Non-Goals

- The MVP does not auto-configure MCP.
- The MVP does not require installing Obsidian.
- The MVP does not require Obsidian CLI to exist.
- Milestone 9 does not require Obsidian backlinks, daily note support, or live Obsidian CLI transport calls.
