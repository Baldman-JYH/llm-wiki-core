# Artifact Equivalence Verification

Date: 2026-06-26

## Purpose

Verify that the current MVP produces artifact-level equivalent LLM Wiki output for local Codex App / CLI usage.

Artifact-level equivalence means the stable Wiki artifacts match the intended structure and behavior: raw source preservation, manifest metadata, source pages, wikilinks, index/log/hot updates, saved insight pages, re-entry context, and lint health.

It does not mean byte-for-byte equality of LLM-authored prose.

## Automated Verification

Automated test:

```text
tests/unit/test_artifact_equivalence_verification.py::test_mvp_artifact_level_equivalence_verification
```

Focused result:

```text
1 passed
```

## Verified Flow

The test runs the complete MVP path in a temporary vault:

1. `init_vault`
2. `detect_transport`
3. create raw source under `.raw/articles/`
4. `ingest_source`
5. `query_wiki`
6. `save_insight`
7. `status_wiki`
8. `continue_wiki`
9. `lint_wiki`

## Verification Matrix

| Layer | Verified checks |
|---|---|
| Structure | `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, source/entity/concept/question/comparison/meta folders, `AGENTS.md` |
| Agent instructions | `AGENTS.md` includes artifact-level equivalence, `llm-wiki ingest`, and resume context trigger text |
| Transport | snapshot exists, filesystem is preferred and implemented, Obsidian CLI is not required |
| Raw source | raw file content remains unchanged after ingest |
| Manifest | source record includes source path, ingested status, fingerprint, and generated page path |
| Source page | source page has source frontmatter, source path, fingerprint, and raw source reference |
| Index/log/hot | ingest and save update stable navigation, operation timeline, and recent context |
| Query | answer cites `[[Karpathy Llm Wiki]]` and does not mutate Wiki files |
| Save | question page is created with frontmatter and durable content |
| Status | reports initialized vault, one source, filesystem runtime transport, and no missing required paths |
| Continue | reads hot/index/log and includes recent save entry |
| Lint | blocker/high/medium/low counts are all zero and a lint report is written |

## Result

The current MVP satisfies artifact-level equivalence for the core local Codex App / CLI Wiki loop.

## Boundaries

- Official `obsidian` CLI transport is optional and verified-only; filesystem remains the artifact-equivalence baseline.
- Claude Code plugin/hooks/subagent behavior is not implemented in the neutral core.
- URL ingest, batch ingest, deep retrieval, vector search, and LLM synthesis are not part of this verification.
- Generated prose is not compared byte-for-byte.
