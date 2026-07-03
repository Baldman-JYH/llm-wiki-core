param(
  [switch]$InstallProjectAdapter,
  [string]$ProjectDestination,
  [switch]$DryRun,
  [switch]$ReplaceClaudeAdapter
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")
$ClaudeSource = Join-Path $RepoRoot "integrations\claude"

function Test-RequiredFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Claude adapter source file not found at `"$Path`"."
  }
}

function Test-FileIdentical {
  param([string]$Source, [string]$Destination)
  if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
    return $false
  }
  return (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
}

function Copy-AdapterFile {
  param([string]$Source, [string]$Destination)

  Test-RequiredFile -Path $Source

  if ($DryRun) {
    Write-Host "DRY RUN: Copy `"$Source`" to `"$Destination`""
    return
  }

  if (Test-Path -LiteralPath $Destination) {
    if (Test-FileIdentical -Source $Source -Destination $Destination) {
      return
    }
    if (-not $ReplaceClaudeAdapter) {
      throw "Claude adapter destination already exists and differs. Re-run with -ReplaceClaudeAdapter to replace it."
    }
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
      throw "Claude adapter destination already exists and differs. Re-run with -ReplaceClaudeAdapter to replace it."
    }
    Remove-Item -LiteralPath $Destination -Force
  }

  $parent = Split-Path -Parent $Destination
  if (-not [string]::IsNullOrWhiteSpace($parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
  Copy-Item -LiteralPath $Source -Destination $Destination
}

function Install-ProjectAdapter {
  if ([string]::IsNullOrWhiteSpace($ProjectDestination)) {
    throw "Claude project adapter install requires -ProjectDestination."
  }

  if (-not (Test-Path -LiteralPath $ProjectDestination -PathType Container)) {
    throw "Claude project adapter destination must be an existing directory."
  }

  $resolvedProject = (Resolve-Path -LiteralPath $ProjectDestination).Path
  Write-Host "Install Claude project adapter into `"$resolvedProject`""

  $targets = @(
    @{ Source = Join-Path $ClaudeSource "CLAUDE.template.md"; Destination = Join-Path $resolvedProject "CLAUDE.md" },
    @{ Source = Join-Path $ClaudeSource "skills\llm-wiki\SKILL.md"; Destination = Join-Path $resolvedProject ".claude\skills\llm-wiki\SKILL.md" },
    @{ Source = Join-Path $ClaudeSource "commands\wiki.md"; Destination = Join-Path $resolvedProject ".claude\commands\wiki.md" },
    @{ Source = Join-Path $ClaudeSource "commands\save.md"; Destination = Join-Path $resolvedProject ".claude\commands\save.md" }
  )

  foreach ($target in $targets) {
    Copy-AdapterFile -Source $target.Source -Destination $target.Destination
  }

  if ($DryRun) {
    return
  }

  Write-Host "Claude project adapter installed"
  Write-Host "Next Claude prompt: /wiki status"
  Write-Host "Next Claude prompt: /save"
}

if (-not $InstallProjectAdapter) {
  throw "Use -InstallProjectAdapter to install the Claude project adapter."
}

Install-ProjectAdapter
