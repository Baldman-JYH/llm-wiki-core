# Obsidian CLI Transport Boundary Rehearsal

Date: 2026-06-26

## Purpose

Verify that Obsidian CLI detection does not cause the MVP to prefer an unimplemented transport.

The current reliable runtime transport is filesystem. Obsidian CLI can be detected and recorded, but actual read/write/search through Obsidian CLI remains outside the MVP.

## Commands Rehearsed

```powershell
llm-wiki init <vault> --purpose "Milestone 16 Obsidian CLI transport boundary rehearsal"
llm-wiki detect-transport <vault> --force
llm-wiki status <vault>
```

## Result

On this machine, Obsidian CLI was detected, but the snapshot correctly kept filesystem as the preferred implemented transport:

```text
detect-transport success
preferred: filesystem
status success
preferred transport: filesystem
SNAPSHOT preferred=filesystem
SNAPSHOT fallback_chain=filesystem
SNAPSHOT obsidian_available=True
SNAPSHOT obsidian_implemented=False
SNAPSHOT filesystem_available=True
SNAPSHOT filesystem_implemented=True
```

## Boundary

`ObsidianCliTransport` exists only as a contract placeholder. Its methods raise `ObsidianCliTransportNotImplementedError` until actual Obsidian CLI read/write/search behavior is implemented and tested.

This keeps the LLM Wiki artifact path honest: current core operations use filesystem transport, while Obsidian CLI remains a future desktop integration boundary.

