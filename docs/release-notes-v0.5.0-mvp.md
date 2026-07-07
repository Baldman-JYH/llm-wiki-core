# Release Notes: v0.5.0-mvp

Date: 2026-07-07

## Status

`v0.5.0-mvp` marks the R5.0 Knowledge Organization Foundation release for `llm-wiki-core`.

This release adds a neutral organization definition boundary while preserving the existing `generic` LLM Wiki behavior. It keeps Karpathy's LLM Wiki pattern canonical: raw sources stay durable, the agent maintains Markdown wiki artifacts, and index/log/hot preserve continuity.

## Included

- Explicit `generic` organization definition.
- Shared frontmatter helper for seed pages.
- Shared scaffold definition for required directories, seed pages, page routes, and lint required paths.
- `llm-wiki init <vault> --purpose "..." --organization generic`.
- Backward-compatible default `llm-wiki init <vault> --purpose "..."` behavior.
- Unsupported organization mode rejection before scaffold files are written.
- Lint required paths sourced from the organization contract.
- Public knowledge organization documentation.
- Capability mapping, roadmap, and roadmap schedule guardrails for R5.0.
- Documentation guard tests for foundation-only support.

## Not Included

- LYT runtime mode remains deferred.
- PARA runtime mode remains deferred.
- Zettelkasten runtime mode remains deferred.
- DragonScale or log-folding memory remains deferred.
- Semantic stale-claim lint remains deferred.
- Comparison workflow helpers remain deferred.
- Vector search, hybrid retrieval, reranking, and qmd integration remain deferred.
- Claude hooks, Claude subagents, and `.claude-plugin` packaging remain deferred.
- Full `claude-obsidian` parity is not claimed.

## Verification

Release verification before publication:

```powershell
python -m pytest tests/unit/test_organization_foundation.py tests/unit/test_init_operation.py tests/unit/test_lint_operation.py tests/unit/test_r5_0_knowledge_organization_docs.py -q
python -m pytest tests/unit/test_r4_2_adapter_parity_baseline_docs.py tests/unit/test_r4_3_claude_adapter_assets.py tests/unit/test_readme_hygiene.py tests/unit/test_release_docs.py tests/unit/test_completion_readiness_docs.py -q
python -m pytest -q
git diff --check
```

Expected result for this release line:

```text
33 passed
37 passed, 4 skipped
267 passed, 10 skipped
```

The skipped tests are POSIX shell execution checks that are expected on Windows. They do not require Windows users to install WSL or Git Bash.

## Release Tag

Local and remote release tag:

```text
v0.5.0-mvp
```

## Archive

The release archive should be produced from the Git tag with `git archive` and stored outside the repository working tree.
