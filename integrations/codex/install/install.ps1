param(
  [string]$VaultPath,
  [string]$Purpose,
  [switch]$DryRun,
  [switch]$InstallUserSkill,
  [string]$SkillDestination,
  [switch]$ReplaceUserSkill
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")
$SkillSource = Join-Path $RepoRoot "integrations\codex\skills\llm-wiki"

function Test-RequiredContent {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Content,

    [Parameter(Mandatory = $true)]
    [string]$Needle
  )

  return $Content.Contains($Needle)
}

function Get-DirectoryFingerprint {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  $items = Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName
  $fingerprint = @(
    foreach ($item in $items) {
    $relativePath = $item.FullName.Substring($Path.Length).TrimStart('\')
    $hash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    "$relativePath|$hash"
  }
  )

  return ,$fingerprint
}

function Test-DirectoriesIdentical {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [Parameter(Mandatory = $true)]
    [string]$Destination
  )

  if (-not (Test-Path -LiteralPath $Destination -PathType Container)) {
    return $false
  }

  $sourceFingerprint = @(Get-DirectoryFingerprint -Path $Source)
  $destinationFingerprint = @(Get-DirectoryFingerprint -Path $Destination)

  if ($sourceFingerprint.Count -ne $destinationFingerprint.Count) {
    return $false
  }

  for ($index = 0; $index -lt $sourceFingerprint.Count; $index++) {
    if ($sourceFingerprint[$index] -ne $destinationFingerprint[$index]) {
      return $false
    }
  }

  return $true
}

function Show-UserSkillNextPrompts {
  Write-Host "Next Codex prompt: check wiki status"
  Write-Host "Next Codex prompt: search wiki for durable knowledge"
}

function Install-UserSkill {
  $resolvedSkillDestination = if ([string]::IsNullOrWhiteSpace($SkillDestination)) {
    Join-Path $HOME ".agents\skills\llm-wiki"
  } else {
    $SkillDestination
  }

  $skillManifest = Join-Path $SkillSource "SKILL.md"
  if (-not (Test-Path -LiteralPath $skillManifest -PathType Leaf)) {
    throw "Codex user skill source manifest not found at `"$skillManifest`"."
  }

  $skillText = Get-Content -LiteralPath $skillManifest -Raw -Encoding UTF8
  if (-not (Test-RequiredContent -Content $skillText -Needle "name: llm-wiki")) {
    throw "Codex user skill source manifest must contain 'name: llm-wiki'."
  }

  if (-not (Test-RequiredContent -Content $skillText -Needle "description:")) {
    throw "Codex user skill source manifest must contain 'description:'."
  }

  if ($DryRun) {
    Write-Host "DRY RUN: Install Codex user skill from `"$SkillSource`" to `"$resolvedSkillDestination`""
    return
  }

  if (Test-Path -LiteralPath $resolvedSkillDestination) {
    if (-not (Test-Path -LiteralPath $resolvedSkillDestination -PathType Container)) {
      throw "Codex user skill destination already exists and differs. Re-run with -ReplaceUserSkill to replace it."
    }

    if (Test-DirectoriesIdentical -Source $SkillSource -Destination $resolvedSkillDestination) {
      Write-Host "Codex user skill already installed at `"$resolvedSkillDestination`""
      Show-UserSkillNextPrompts
      return
    }

    if (-not $ReplaceUserSkill) {
      throw "Codex user skill destination already exists and differs. Re-run with -ReplaceUserSkill to replace it."
    }

    Remove-Item -LiteralPath $resolvedSkillDestination -Recurse -Force
  }

  $destinationParent = Split-Path -Parent $resolvedSkillDestination
  if (-not [string]::IsNullOrWhiteSpace($destinationParent)) {
    New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
  }

  Copy-Item -LiteralPath $SkillSource -Destination $resolvedSkillDestination -Recurse
  Write-Host "Codex user skill installed at `"$resolvedSkillDestination`""
  Show-UserSkillNextPrompts
}

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

if ($InstallUserSkill) {
  Install-UserSkill
  return
}

if ([string]::IsNullOrWhiteSpace($VaultPath) -or [string]::IsNullOrWhiteSpace($Purpose)) {
  throw "Repo-local install requires both -VaultPath and -Purpose."
}

Invoke-OrShow "python -m pip install -e `"$RepoRoot`"" { python -m pip install -e "$RepoRoot" }
Invoke-OrShow "llm-wiki init `"$VaultPath`" --purpose `"$Purpose`"" { llm-wiki init "$VaultPath" --purpose "$Purpose" }
Invoke-OrShow "llm-wiki detect-transport `"$VaultPath`"" { llm-wiki detect-transport "$VaultPath" }

Write-Host "Next: llm-wiki status `"$VaultPath`""
Write-Host "Next: llm-wiki continue `"$VaultPath`""

Write-Host "llm-wiki Codex adapter initialized for $VaultPath"
