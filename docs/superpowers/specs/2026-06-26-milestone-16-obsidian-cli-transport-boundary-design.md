# Milestone 16 Obsidian CLI Transport Boundary Design

## Goal

Make the Obsidian CLI transport boundary explicit: the system may detect an Obsidian CLI executable, but it must not prefer or route operations through Obsidian CLI until actual read/write/search behavior is implemented.

## Context

Previous milestones treated Obsidian CLI as an optional preferred transport when a local `obsidian-cli` or `obsidian` executable was found. That is too optimistic for the current MVP because the core only implements filesystem transport operations.

The Karpathy LLM Wiki pattern values durable artifacts over tool-specific theatrics. A detected desktop tool is useful context, but the current reliable artifact path is filesystem read/write/search.

## Scope

Implement:

- transport snapshot fields that separate detection from implementation;
- `obsidian-cli` recorded as `available: true` but `implemented: false` when executable is found;
- `filesystem` recorded as both `available: true` and `implemented: true`;
- fresh detection prefers `filesystem` until Obsidian CLI transport is implemented;
- an Obsidian CLI transport placeholder that exposes the intended boundary and raises a clear error if used;
- documentation and rehearsal evidence for the boundary.

## Non-Goals

- Do not implement actual Obsidian CLI read/write/search calls.
- Do not invoke Obsidian CLI from core operations.
- Do not require Obsidian CLI to be installed.
- Do not install or configure Obsidian.
- Do not modify global Codex configuration.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Design Decision

`preferred` means "safe to use for current core operations", not merely "best available desktop integration". Therefore `filesystem` remains preferred while Obsidian CLI is contract-only.

The snapshot can still record Obsidian CLI availability. That preserves forward compatibility and makes future actual integration straightforward without misleading current users.

## Expected Snapshot Semantics

When Obsidian CLI is missing:

```json
{
  "preferred": "filesystem",
  "available": {
    "obsidian-cli": {
      "available": false,
      "implemented": false
    },
    "filesystem": {
      "available": true,
      "implemented": true
    }
  }
}
```

When Obsidian CLI is detected:

```json
{
  "preferred": "filesystem",
  "available": {
    "obsidian-cli": {
      "available": true,
      "implemented": false,
      "executable": "..."
    },
    "filesystem": {
      "available": true,
      "implemented": true
    }
  }
}
```

