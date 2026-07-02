# Adapter Packaging Plan

This document defines the Codex adapter packaging strategy through R4.1.

## Packaging Goals

Codex App and Codex CLI users should be able to use the same core LLM Wiki workflow that the Claude Code + Obsidian reference implementation demonstrates: initialize a vault, ingest raw sources, search and query the wiki, lint it, save durable insights, and maintain `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, and `.raw/.manifest.json`.

The neutral core must not depend on Codex adapter behavior.

## Repo-Local Mode

Repo-local mode remains the baseline install mode. The user runs the installer from this repository, the installer performs editable package installation, initializes the target vault, detects transport, and prints re-entry commands.

## User-Level Skill Mode

User-level skill mode is the reusable Codex skill path. R4.1 adds explicit user-level skill installation. The documented default destination is `$HOME/.agents/skills/llm-wiki`, and the install path stays opt-in through `-InstallUserSkill` or `--install-user-skill`. R4.1 does not edit global Codex configuration automatically.

## Plugin Packaging Decision

Plugin packaging is a future target. R4.1 does not publish a marketplace-grade Codex plugin.

A future plugin may include skill metadata, command mapping docs, install guidance, and adapter verification. It must still call neutral core commands instead of redefining LLM Wiki behavior.

## Windows Support

Windows support must be native PowerShell. It must not require WSL or Git Bash.

## macOS And Linux Support

macOS and Linux support use the portable shell installer. Shell scripts remain thin wrappers around core commands.

## Non-Goals

- Do not publish to a marketplace in R4.0.
- Do not generate Claude-specific plugin files.
- Do not modify global Codex configuration automatically.
- Do not move domain behavior into the Codex adapter.
