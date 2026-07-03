# Claude Adapter Install

R4.3 installs Claude adapter assets into a project-local destination.

It does not edit user-global Claude settings automatically.

## PowerShell

```powershell
.\install.ps1 -InstallProjectAdapter -ProjectDestination <project> -DryRun
.\install.ps1 -InstallProjectAdapter -ProjectDestination <project>
.\install.ps1 -InstallProjectAdapter -ProjectDestination <project> -ReplaceClaudeAdapter
```

## POSIX Shell

```sh
./install.sh --install-project-adapter --project-destination <project> --dry-run
./install.sh --install-project-adapter --project-destination <project>
./install.sh --install-project-adapter --project-destination <project> --replace-claude-adapter
```

## Installed Files

- `CLAUDE.md`
- `.claude/skills/llm-wiki/SKILL.md`
- `.claude/commands/wiki.md`
- `.claude/commands/save.md`

No active hooks are installed.

No subagents are installed.

No `.claude/settings.json` file is generated.

No user-global `~/.claude` files are modified.

## Verification

Start Claude Code in the target project and try:

- `/wiki status`
- `/wiki search durable knowledge`
- `/save`
