# Codex Adapter

This directory contains Codex App and Codex CLI integration assets.

The adapter calls into neutral `llm-wiki` core commands instead of redefining LLM Wiki behavior.

## Repo-local mode

Use repo-local mode when working from this repository:

```powershell
integrations/codex/install/install.ps1 -VaultPath <vault> -Purpose "Research workflow"
```

```sh
integrations/codex/install/install.sh <vault> "Research workflow"
```

## User-level skill mode

User-level skill mode copies or installs `integrations/codex/skills/llm-wiki` into a user's Codex skills directory.

R4.0 documents this mode but does not automatically mutate global Codex configuration.

## Verification

After setup, verify that Codex can trigger status, continue, ingest, search, query, save, and lint behavior through natural language.
