# R2 Obsidian CLI Transport Report

Date: 2026-06-26

Status: complete.

R2 adds a conservative official `obsidian` CLI transport path for local desktop workflows. The official `obsidian` CLI is runtime eligible only after vault binding and read/write/append/list/search capability probes pass.

The legacy `obsidian-cli` command is still detected as legacy metadata, but it is not used by the R2 runtime.

Automated verification uses a fake runner so tests do not require Obsidian to be installed, running, or configured. Filesystem fallback remains the safe path in all unverified cases.
