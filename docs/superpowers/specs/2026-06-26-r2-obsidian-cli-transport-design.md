# R2 Obsidian CLI Transport Design

Date: 2026-06-26

## Goal

Implement a conservative official Obsidian CLI transport path for `llm-wiki-core`, so local Codex App and Codex CLI workflows can use Obsidian's desktop CLI for vault read/write/search when it is actually usable, while preserving filesystem transport as the safe fallback.

R2 must keep the project aligned with Karpathy's LLM Wiki idea: the durable artifact is the Markdown Wiki, not a chat transcript, not an Obsidian-only database, and not a tool-specific integration.

## Context

Current state after R1:

- `filesystem` is the only implemented runtime transport.
- `obsidian-cli` is detected as metadata but marked `implemented: false`.
- `ObsidianCliTransport` is a placeholder that raises a clear not-implemented error.
- Runtime selection always falls back to filesystem even if an Obsidian CLI executable exists.

Reference implementation context:

- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) treats Obsidian CLI as a default desktop transport in its v1.7 Compound Vault design.
- That repository's older `wiki-cli` skill uses an `obsidian-cli <vault> <path>` recipe style.
- Official Obsidian CLI documentation now describes the official `obsidian` command, name/value parameters, and a requirement that the Obsidian app be running.

External source of truth for R2:

- [Obsidian CLI - Obsidian Help](https://obsidian.md/help/cli)

Important official constraints from that source:

- Obsidian CLI requires a recent installer and must be enabled in Obsidian settings.
- The CLI is invoked through `obsidian`, not the older community `obsidian-cli` command.
- Obsidian CLI depends on the desktop app; it is not a pure headless transport.
- Commands use name/value style arguments such as `query="..."`, `path="..."`, and content arguments.

## Design Decision

Use **official `obsidian` CLI first**, and treat community `obsidian-cli` as legacy metadata only in R2.

R2 should not blindly promote any detected binary to runtime use. A detected CLI becomes runtime eligible only when all of these are true:

1. The executable is the official `obsidian` command.
2. The command can be invoked for basic version/help probing.
3. A vault selector can be resolved for the target vault.
4. The selector can read a known sentinel file from the target vault, such as `wiki/index.md`.
5. Required capabilities are verified: read, write/create-overwrite, append, list files, and search.
6. The transport snapshot records `available: true`, `implemented: true`, and capability metadata.

If any condition fails, runtime selection uses filesystem and records a warning.

## Scope

R2 includes:

- an official Obsidian CLI command runner abstraction;
- command builder functions for read, write, append, list markdown files, search text, and existence checks;
- capability probe logic that does not rely on user interaction;
- transport snapshot fields for official CLI vs legacy CLI;
- runtime selection that can prefer Obsidian CLI only when implemented and verified;
- filesystem fallback when Obsidian CLI is missing, disabled, unverified, or command execution fails during probing;
- tests using fake runners, not real Obsidian desktop state;
- documentation for setup, boundary, and troubleshooting.

R2 does not include:

- MCP transport;
- REST API transport;
- URL ingest;
- batch ingest;
- hybrid retrieval;
- vector search;
- Obsidian daily note workflow;
- backlinks;
- Bases resolved views;
- per-file advisory locking;
- Claude Code hooks or subagents;
- mutation of global Codex configuration;
- modification of `claude-obsidian`.

## Architecture

### 1. Command Runner

Create a small runner boundary for subprocess execution.

Responsibilities:

- accept argv as a list of strings;
- run with UTF-8 text mode;
- capture stdout, stderr, and return code;
- enforce timeout;
- never invoke a shell;
- expose a fake-runner-friendly interface for tests.

The runner must keep Windows PowerShell, macOS shell, Linux shell, spaces, and non-ASCII paths in mind by avoiding string-built shell commands.

### 2. Official Obsidian CLI Profile

Create an explicit profile for the official CLI.

Responsibilities:

- executable name/path: official `obsidian`;
- argument syntax: name/value tokens;
- vault selector: resolved separately from filesystem path;
- content encoding: encode multiline content in the format accepted by official CLI, while preserving UTF-8 strings in Python;
- command construction for:
  - read;
  - create/overwrite;
  - append;
  - files/list;
  - search;
  - help/version probes.

The command builder should be tested independently from subprocess execution.

### 3. Vault Binding Probe

The highest risk is accidentally talking to the wrong Obsidian vault. R2 must therefore verify binding before runtime promotion.

Initial default selector:

- derive a candidate selector from the vault root folder name;
- allow future manual override through snapshot metadata.

Required probe:

- attempt to read `wiki/index.md` through the official CLI using the candidate selector;
- verify the output contains an expected initialized-vault signal such as `# Wiki Index`;
- if this fails, the CLI is not runtime eligible and filesystem remains preferred.

This keeps default behavior safe for users with multiple Obsidian vaults.

### 4. Capability Probe

R2 needs capability metadata, not just `available: true`.

Snapshot should be able to record:

```json
{
  "available": {
    "obsidian": {
      "available": true,
      "implemented": true,
      "executable": "...",
      "reason": "official Obsidian CLI verified for this vault",
      "capabilities": {
        "read": true,
        "write": true,
        "append": true,
        "list": true,
        "search": true
      },
      "vault_selector": "example-vault"
    },
    "obsidian-cli": {
      "available": true,
      "implemented": false,
      "reason": "legacy community CLI detected; not used by R2 runtime"
    },
    "filesystem": {
      "available": true,
      "implemented": true
    }
  }
}
```

If any required capability is false, `preferred` must remain `filesystem`.

### 5. Runtime Selection

Runtime selection should become capability-aware:

- missing snapshot: filesystem;
- invalid snapshot: filesystem with warning;
- preferred filesystem: filesystem;
- preferred official obsidian with verified capabilities: Obsidian CLI transport;
- preferred official obsidian without verified capabilities: filesystem with warning;
- legacy `obsidian-cli`: filesystem with warning;
- unknown preferred transport: filesystem with warning.

R2 should keep all existing operations using the neutral transport interface:

- `query`;
- `lint`;
- `status`;
- `continue`;
- `ingest`;
- `save`.

`init` may continue writing the initial scaffold through filesystem. This is acceptable because the vault does not yet have a verified Obsidian CLI binding before initialization.

### 6. Fallback Behavior

R2 fallback happens in two layers:

1. Detection/probe fallback: if CLI cannot be verified, runtime uses filesystem.
2. Runtime selector fallback: if snapshot points at a transport that is unavailable, unimplemented, or missing capability metadata, runtime uses filesystem and emits warnings.

R2 should avoid silent per-write fallback inside a single mutating operation unless the implementation can make warnings visible. A hidden fallback after a partial CLI write could make conflict diagnosis harder.

If a selected Obsidian CLI command fails during an operation, the operation should fail clearly. The user can re-run `detect-transport --force`; if probing fails, the next run will return to filesystem.

This conservative rule is safer than silently mixing two write transports in one operation.

## Error Handling

Add an Obsidian CLI transport error hierarchy:

- command unavailable;
- command timed out;
- non-zero exit;
- vault binding failed;
- capability missing;
- parse error for files/search output.

Errors should include:

- transport name;
- operation name;
- command label, not raw secret-bearing shell string;
- exit code when available;
- stderr summary when available.

CLI `--json` from R1 should make these errors machine-readable through the existing structured error path.

## Testing Strategy

Tests must be hermetic. They must not require Obsidian to be installed, running, or configured.

Required tests:

- command builder emits expected argv lists for read/write/append/list/search;
- fake runner success for read/write/append/list/search;
- fake runner non-zero exit maps to transport error;
- multiline UTF-8 content is preserved through command construction;
- path traversal and absolute paths are rejected before command execution;
- detection records official `obsidian` as available when fake executable is found;
- detection records legacy `obsidian-cli` as legacy/unimplemented;
- detection keeps preferred filesystem when capability probe fails;
- detection can prefer official obsidian when all fake probes pass;
- runtime selector returns Obsidian CLI transport only with verified capability metadata;
- runtime selector falls back with warning for legacy, unimplemented, invalid, or capability-incomplete snapshots;
- existing filesystem-only artifact equivalence test remains green;
- docs describe desktop-only boundary and fallback.

Optional local smoke, not required for CI:

- if a developer has Obsidian 1.12+ installed and enabled, run `llm-wiki detect-transport <vault> --force` against a real vault and document the result.

## Documentation Updates

Update these docs during implementation:

- `docs/transport-contract.md`;
- `docs/roadmap-schedule.md`;
- `docs/user-guide.md`;
- `docs/obsidian-cli-transport-boundary-rehearsal.md` or a new R2 rehearsal document;
- README if user-facing setup changes are meaningful;
- `codex_doc/project_understanding_progress.md` after each completed stage.

## Open Design Choices Resolved For R2

- Official `obsidian` is the only runtime candidate in R2.
- Legacy `obsidian-cli` remains detected but unimplemented.
- The initial vault selector candidate is the vault root folder name.
- Runtime promotion requires sentinel read verification against `wiki/index.md`.
- Real Obsidian desktop is not required in automated tests.
- `init` remains filesystem-based.

## Acceptance Criteria

R2 is complete when:

- all new behavior is covered by tests that fail before implementation and pass after implementation;
- `python -m pytest -q` passes;
- official Obsidian CLI can be represented as an implemented transport only after fake capability probes pass;
- filesystem remains the safe fallback in all unverified cases;
- `v0.1.0-mvp` tag remains unchanged;
- `claude-obsidian` remains unmodified;
- progress documentation is updated in `codex_doc`.
