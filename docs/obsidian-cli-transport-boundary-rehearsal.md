# Obsidian CLI Transport Boundary Rehearsal

> Historical note: this rehearsal documents the MVP/R1 boundary before R2. Current R2 behavior is documented in `docs/r2-obsidian-cli-transport-report.md`: official `obsidian` CLI can be runtime eligible only after vault binding and read/write/append/list/search capability probes pass.

Date: 2026-06-26

## Purpose

Verify that Obsidian CLI detection does not cause the MVP to prefer an unimplemented transport.

For the original MVP boundary, the reliable runtime transport was filesystem. After R2, the official `obsidian` CLI is optional and verified-only, while filesystem remains the fallback.

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

This historical rehearsal predates the R2 `ObsidianCliTransport` implementation. R2 replaced the placeholder with a fake-runner-tested transport that is selected only after capability verification.

This keeps the LLM Wiki artifact path honest: current core operations use filesystem transport, while Obsidian CLI remains a future desktop integration boundary.
