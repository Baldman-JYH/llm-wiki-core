# Milestone 3 Transport Design

## Goal

Implement MVP transport detection so future operations can choose a stable read/write channel for a local LLM Wiki vault.

## Confirmed Approach

Use Python core detection plus a CLI subcommand:

- Core API: `detect_transport(vault_root, force=False)`
- CLI: `llm-wiki detect-transport <vault> [--force]`

The snapshot is written to `.vault-meta/transport.json`.

## Detection Rules

- Filesystem transport is always available.
- Obsidian CLI transport is available when either `obsidian-cli` or `obsidian` is found on `PATH`.
- Preferred transport is `obsidian-cli` when available, otherwise `filesystem`.
- Fallback chain is always `["obsidian-cli", "filesystem"]`.

## Snapshot Shape

```json
{
  "schema_version": 1,
  "detected_at": "2026-06-25T00:00:00+08:00",
  "platform": "Windows",
  "vault_root": "D:/path/to/vault",
  "preferred": "filesystem",
  "fallback_chain": ["obsidian-cli", "filesystem"],
  "available": {
    "obsidian-cli": {
      "available": false,
      "executable": null
    },
    "filesystem": {
      "available": true,
      "executable": null
    }
  },
  "manual_override": null
}
```

## Boundaries

- Do not install Obsidian or Obsidian CLI.
- Do not call Obsidian CLI during detection.
- Do not implement file read/write/search transport operations yet.
- Do not implement MCP or REST transports.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Verification

Tests should validate:

- no CLI present -> filesystem preferred
- fake `obsidian-cli` on PATH -> obsidian-cli preferred
- snapshot file is valid JSON and uses vault-relative location `.vault-meta/transport.json`
- CLI command writes snapshot and prints concise summary
- rerun without `force` can reuse existing snapshot
- rerun with `force` refreshes snapshot
