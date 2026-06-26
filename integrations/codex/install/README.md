# Installers

Repo-local installer entrypoints for Codex App / CLI usage.

PowerShell:

```powershell
.\install.ps1 -VaultPath D:\path\to\vault -Purpose "Research workflow"
.\install.ps1 -VaultPath D:\path\to\vault -Purpose "Research workflow" -DryRun
```

macOS / Linux shell:

```sh
./install.sh /path/to/vault "Research workflow"
./install.sh --dry-run /path/to/vault "Research workflow"
```

The installers run local editable package installation, initialize the vault, and detect transport. They print `status` and `continue` as recommended next steps.
