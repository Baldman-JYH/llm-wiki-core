# Project Skeleton Plan

本文件定义未来实现阶段的项目目录计划。

当前阶段只规划目录，不创建代码骨架。

## Design Goals

项目骨架应支持：

- 中性 core。
- Codex adapter。
- 未来 Claude adapter。
- Windows 原生实现。
- macOS 本地实现。
- 文档驱动开发。
- MVP parity tests。

## Proposed Skeleton

```text
llm-wiki-core/
├── README.md
├── CONTEXT.md
├── pyproject.toml
├── llm_wiki_core/
│   ├── __init__.py
│   ├── cli.py
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── status.py
│   │   ├── continue_.py
│   │   ├── ingest.py
│   │   ├── query.py
│   │   ├── lint.py
│   │   ├── save.py
│   │   └── detect_transport.py
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── manifest.py
│   │   ├── frontmatter.py
│   │   └── wikilinks.py
│   ├── transport/
│   │   ├── __init__.py
│   │   ├── filesystem.py
│   │   ├── obsidian_cli.py
│   │   └── snapshot.py
│   ├── vault/
│   │   ├── __init__.py
│   │   ├── paths.py
│   │   ├── scaffold.py
│   │   ├── index.py
│   │   ├── log.py
│   │   └── hot.py
│   └── validation/
│       ├── __init__.py
│       ├── lint_report.py
│       └── parity.py
├── integrations/
│   ├── codex/
│   │   ├── README.md
│   │   ├── AGENTS.template.md
│   │   ├── skills/
│   │   ├── plugin/
│   │   └── install/
│   │       ├── install.ps1
│   │       └── install.sh
│   └── claude/
│       └── README.md
├── templates/
│   ├── wiki/
│   └── pages/
├── tests/
│   ├── fixtures/
│   ├── unit/
│   └── parity/
└── docs/
```

## Skeleton Boundaries

First implementation should not fill every file with full logic.

Recommended first implementation:

- Create package directories.
- Create test fixture directories.
- Create placeholder docs for integrations.
- Add minimal project metadata.
- Add no full ingest/query/lint logic until operation-specific tests are planned.

## Core Package

`llm_wiki_core/` owns domain logic:

- operations。
- schema。
- transport。
- vault file manipulation。
- validation。

It must not import Codex adapter code.

## Integrations

`integrations/codex/` owns:

- Codex-facing instructions。
- Codex skill/plugin metadata。
- install plans。
- command mapping docs。

`integrations/claude/` is reserved for future Claude adapter work.

## Tests

`tests/fixtures/` follows `docs/test-fixture-plan.md`:

- `f0-empty`
- `f1-fresh-vault`
- `f2-single-source`
- `f3-existing-knowledge`
- `f4-broken-wiki`

No fixture should require network access.

## Naming Notes

- Python package name: `llm_wiki_core`。
- Project directory name: `llm-wiki-core`。
- CLI name can be decided later. Candidate: `llm-wiki`。

## Non-Goals

- This plan does not require immediate creation of code files.
- This plan does not define exact Python APIs.
- This plan does not implement installer scripts.
- This plan does not copy `claude-obsidian`.
