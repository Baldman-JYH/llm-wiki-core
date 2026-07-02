# Installers

Repo-local installer entrypoints for Codex App / CLI usage.

## Repo-Local Install

PowerShell:

```powershell
.\install.ps1 -VaultPath <vault> -Purpose "Research workflow"
.\install.ps1 -VaultPath <vault> -Purpose "Research workflow" -DryRun
```

macOS / Linux shell:

```sh
./install.sh <vault> "Research workflow"
./install.sh --dry-run <vault> "Research workflow"
```

The installers run local editable package installation, initialize the vault, and detect transport. They print `status` and `continue` as recommended next steps.

Windows support is native PowerShell and does not require compatibility shell layers.

## User-Level Skill Install

R4.1 documents explicit user-level skill installation. This mode is opt-in and does not edit global Codex configuration automatically.

Default skill destination:

```text
$HOME/.agents/skills/llm-wiki
```

PowerShell:

```powershell
.\install.ps1 -InstallUserSkill -DryRun
.\install.ps1 -InstallUserSkill
```

macOS / Linux shell:

```sh
./install.sh --install-user-skill --dry-run
./install.sh --install-user-skill
```

Use `-SkillDestination <path>` or `--skill-destination <path>` for tests or advanced installs.

After the installer copies the skill, start a new Codex session so the newly installed skill is picked up cleanly.
