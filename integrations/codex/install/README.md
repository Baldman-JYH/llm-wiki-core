# Installers

Repo-local installer entrypoints for Codex App / CLI usage.

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
