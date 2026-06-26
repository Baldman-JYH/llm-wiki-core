param(
  [Parameter(Mandatory = $true)]
  [string]$VaultPath,

  [Parameter(Mandatory = $true)]
  [string]$Purpose,

  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")

function Invoke-OrShow {
  param(
    [Parameter(Mandatory = $true)]
    [string]$CommandText,

    [Parameter(Mandatory = $true)]
    [scriptblock]$Action
  )

  if ($DryRun) {
    Write-Host "DRY RUN: $CommandText"
    return
  }

  Write-Host $CommandText
  & $Action
}

Invoke-OrShow "python -m pip install -e `"$RepoRoot`"" { python -m pip install -e "$RepoRoot" }
Invoke-OrShow "llm-wiki init `"$VaultPath`" --purpose `"$Purpose`"" { llm-wiki init "$VaultPath" --purpose "$Purpose" }
Invoke-OrShow "llm-wiki detect-transport `"$VaultPath`"" { llm-wiki detect-transport "$VaultPath" }

Write-Host "Next: llm-wiki status `"$VaultPath`""
Write-Host "Next: llm-wiki continue `"$VaultPath`""

Write-Host "llm-wiki Codex adapter initialized for $VaultPath"
