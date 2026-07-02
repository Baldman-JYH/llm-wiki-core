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

function Get-NormalizedPath {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  $fullPath = [System.IO.Path]::GetFullPath($Path)
  $rootPath = [System.IO.Path]::GetPathRoot($fullPath)
  while (
    $fullPath.Length -gt $rootPath.Length -and
    ($fullPath.EndsWith("\") -or $fullPath.EndsWith("/"))
  ) {
    $fullPath = $fullPath.Substring(0, $fullPath.Length - 1)
  }

  return $fullPath
}

function Test-SamePath {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Left,

    [Parameter(Mandatory = $true)]
    [string]$Right
  )

  $normalizedLeft = Get-NormalizedPath -Path $Left
  $normalizedRight = Get-NormalizedPath -Path $Right
  return [string]::Equals($normalizedLeft, $normalizedRight, [System.StringComparison]::OrdinalIgnoreCase)
}

function Assert-SafeReplaceDestination {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Destination
  )

  if ([string]::IsNullOrWhiteSpace($Destination)) {
    throw "Refusing to replace Codex user skill destination because it is empty."
  }

  $trimmedDestination = $Destination.Trim()
  if ($trimmedDestination -eq "." -or $trimmedDestination -eq "..") {
    throw "Refusing to replace Codex user skill destination `"$Destination`" because it is outside the allowed llm-wiki directory boundary."
  }

  $normalizedDestination = Get-NormalizedPath -Path $trimmedDestination
  $rootPath = Get-NormalizedPath -Path ([System.IO.Path]::GetPathRoot($normalizedDestination))
  $homePath = Get-NormalizedPath -Path $HOME
  $agentsPath = Get-NormalizedPath -Path (Join-Path $HOME ".agents")
  $skillsPath = Get-NormalizedPath -Path (Join-Path $HOME ".agents\skills")

  if (
    (Test-SamePath -Left $normalizedDestination -Right $rootPath) -or
    (Test-SamePath -Left $normalizedDestination -Right $homePath) -or
    (Test-SamePath -Left $normalizedDestination -Right $agentsPath) -or
    (Test-SamePath -Left $normalizedDestination -Right $skillsPath)
  ) {
    throw "Refusing to replace Codex user skill destination `"$Destination`" because it is outside the allowed llm-wiki directory boundary."
  }

  if ([System.IO.Path]::GetFileName($normalizedDestination) -ne "llm-wiki") {
    throw "Refusing to replace Codex user skill destination `"$Destination`" because its leaf directory must be `"llm-wiki`"."
  }
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

    Assert-SafeReplaceDestination -Destination $resolvedSkillDestination
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
