# Archive Manifest

Date: 2026-06-26

## Release

- Release: `v0.1.0-mvp`
- Archive name: `llm-wiki-core-v0.1.0-mvp.zip`
- Archive method: `git archive`
- Checksum: SHA256 stored beside the generated archive.

## Current Release Archive

- Release: `v0.5.0-mvp`
- Archive name: `llm-wiki-core-v0.5.0-mvp.zip`
- Archive method: `git archive`
- Checksum: SHA256 stored beside the generated archive.
- Artifact location: outside the repository working tree, for example `<release-artifacts>/llm-wiki-core-v0.5.0-mvp.zip`.

## Previous R4.3 Release Archive

- Release: `v0.4.3-mvp`
- Archive name: `llm-wiki-core-v0.4.3-mvp.zip`
- Archive method: `git archive`
- Checksum: SHA256 stored beside the generated archive.
- Artifact location: outside the repository working tree, for example `<release-artifacts>/llm-wiki-core-v0.4.3-mvp.zip`.

## Previous R4 Release Archive

- Release: `v0.4.0-mvp`
- Archive name: `llm-wiki-core-v0.4.0-mvp.zip`
- Archive method: `git archive`
- Checksum: SHA256 stored beside the generated archive.

## Archive Policy

The release archive is generated from the local Git tag:

```powershell
git archive --format=zip --output <release-artifacts>/llm-wiki-core-v0.5.0-mvp.zip v0.5.0-mvp
```

This ensures the archive includes tracked release content and excludes runtime state.

## Exclusions

- exclude .git
- exclude generated caches
- exclude `__pycache__/`
- exclude `.pytest_cache/`
- exclude `*.egg-info/`
- exclude `build/`
- exclude local virtual environments

## Expected Contents

- `llm_wiki_core/`
- `integrations/codex/`
- `docs/`
- `tests/`
- `pyproject.toml`
- `README.md`
- `CONTEXT.md`

## Verification

After archive creation:

1. Verify the archive exists.
2. Generate SHA256.
3. Verify `claude-obsidian` remains untouched.
4. Verify no generated caches remain in the working tree.
