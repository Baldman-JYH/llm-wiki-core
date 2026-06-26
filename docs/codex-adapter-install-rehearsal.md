# Codex Adapter Install Rehearsal

Date: 2026-06-26

## Purpose

Verify that the repo-local Codex adapter installer creates a vault that Codex App / CLI can immediately discover and operate through `AGENTS.md` plus the installed `llm-wiki` command.

This rehearsal focuses on the adapter entry path, not new core behavior. The durable artifact loop remains owned by the neutral core operations.

## Environment

- OS shell: Windows PowerShell
- Installer: `integrations/codex/install/install.ps1`
- Python install mode: editable install with `python -m pip install -e <repo>`
- Temporary vault: `C:\Users\ADMINI~1\AppData\Local\Temp\llm-wiki-core-m15-d29e0efe5b664405a7f74377858e0d1e`
- Transport observed: `obsidian-cli` preferred, with filesystem fallback available through the transport snapshot

## Commands Rehearsed

```powershell
.\integrations\codex\install\install.ps1 `
  -VaultPath <vault> `
  -Purpose "Milestone 15 Codex adapter install rehearsal"

llm-wiki status <vault>
llm-wiki continue <vault>
llm-wiki lint <vault>
```

The installer executed:

```text
python -m pip install -e "D:\ai\llmWiki\llm-wiki-core"
llm-wiki init "<vault>" --purpose "Milestone 15 Codex adapter install rehearsal"
llm-wiki detect-transport "<vault>"
```

## Successful Result

The installer completed successfully and printed the re-entry hints:

```text
Next: llm-wiki status "<vault>"
Next: llm-wiki continue "<vault>"
llm-wiki Codex adapter initialized for <vault>
```

Post-install checks succeeded:

```text
status success
continue success
lint success
blocker: 0
high: 0
medium: 0
low: 0
```

The generated `AGENTS.md` contained:

- `llm-wiki status`
- `llm-wiki continue`
- `llm-wiki ingest`
- `set up wiki`
- `check wiki status`
- `resume wiki context`
- `artifact-level equivalence`

## Findings Fixed During This Milestone

- `llm-wiki init` now writes Codex command discovery and natural language trigger mapping into generated `AGENTS.md`.
- `integrations/codex/COMMANDS.md` table rows are now well-formed Markdown rows.

## Boundary

This rehearsal does not install global Codex skills, does not modify user-level Codex configuration, and does not publish a plugin. It verifies the repo-local adapter path only.

## Cleanup Notes

The temporary rehearsal vault and editable-install generated metadata should be removed after verification. These are generated artifacts and should not be treated as source changes.

