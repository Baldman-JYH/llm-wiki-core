# Generic Mode Structure

本文件定义 MVP 阶段的 generic organization mode。

Generic mode 是第一阶段唯一必需组织模式。它对齐 Karpathy LLM Wiki pattern 和 `claude-obsidian` 的基础目录结构，不要求用户在 LYT、PARA 或 Zettelkasten 之间做选择。

## 设计原则

- 先证明 LLM Wiki 闭环，而不是先引入复杂组织方法论。
- 目录应服务 Raw Source、Wiki、Schema 三层结构。
- 页面路径应稳定、可读、适合 Obsidian 浏览。
- 文件名优先人类可读。
- Wikilinks 优先使用页面标题，不依赖绝对路径。

## Vault Root

MVP vault root 应包含：

```text
vault/
├── .raw/
├── wiki/
└── AGENTS.md 或其他 adapter 生成的项目指令文件
```

`AGENTS.md` 是 Codex adapter 目标文件。其他 adapter 可以生成自己的指令文件，但不能改变 core schema。

## Raw Source Layer

```text
.raw/
├── .manifest.json
├── articles/
├── transcripts/
├── notes/
└── assets/
```

MVP 必需：

- `.raw/.manifest.json`

MVP 可选创建：

- `.raw/articles/`
- `.raw/transcripts/`
- `.raw/notes/`
- `.raw/assets/`

Raw Source 层只读。Agent 不得修改来源文件。

## Wiki Layer

```text
wiki/
├── index.md
├── log.md
├── hot.md
├── overview.md
├── sources/
├── entities/
│   └── _index.md
├── concepts/
│   └── _index.md
├── questions/
├── comparisons/
└── meta/
```

## Required Pages

MVP scaffold 必须创建：

| 页面 | 说明 |
|---|---|
| `wiki/index.md` | Master catalog。查询时先读它。 |
| `wiki/log.md` | 操作时间线。新条目追加到顶部。 |
| `wiki/hot.md` | 近期上下文缓存。应保持简短。 |
| `wiki/overview.md` | Wiki 的高层摘要。MVP 可为 seed 版本。 |

## Required Folders

MVP scaffold 必须创建：

| 目录 | 说明 |
|---|---|
| `wiki/sources/` | 每个 Raw Source 的摘要页。 |
| `wiki/entities/` | 人、组织、产品、仓库等实体页。 |
| `wiki/concepts/` | 概念、模式、框架页。 |
| `wiki/questions/` | 有长期价值的查询回答。 |
| `wiki/comparisons/` | 对比分析页，MVP 可为空。 |
| `wiki/meta/` | lint report、dashboard、约定等 meta 页面。 |

## Optional Sub-Indexes

MVP 推荐创建：

```text
wiki/entities/_index.md
wiki/concepts/_index.md
```

其他 sub-index 可以后续按需要创建。

## Filename Rules

MVP 使用人类可读文件名：

```text
wiki/concepts/LLM Wiki Pattern.md
wiki/entities/Andrej Karpathy.md
wiki/sources/Karpathy LLM Wiki Gist.md
```

规则：

- Markdown 文件使用 `.md`。
- 页面文件名应尽量唯一。
- 文件名允许空格。
- 文件名不应包含路径分隔符、控制字符或平台保留字符。
- Windows 保留名应避免，例如 `CON.md`、`PRN.md`。

## Page Type Routing

| 页面类型 | 默认目录 |
|---|---|
| `source` | `wiki/sources/` |
| `entity` | `wiki/entities/` |
| `concept` | `wiki/concepts/` |
| `question` | `wiki/questions/` |
| `comparison` | `wiki/comparisons/` |
| `meta` | `wiki/meta/` 或 `wiki/` 根部特殊文件 |
| `overview` | `wiki/overview.md` |

## Frontmatter Minimum

所有 Wiki 页面必须有 flat YAML frontmatter。

MVP 最小字段：

```yaml
---
type: concept
title: "Page Title"
created: 2026-06-25
updated: 2026-06-25
status: seed
---
```

推荐字段：

```yaml
tags:
  - wiki/concept
related:
  - "[[Other Page]]"
sources:
  - "[[Source Page]]"
```

## Hot Cache Format

`wiki/hot.md` 应保持缓存语义，不是日志。

MVP 格式：

```markdown
---
type: meta
title: "Hot Cache"
updated: 2026-06-25T00:00:00+08:00
---

# Recent Context

## Last Updated
2026-06-25 — [what changed]

## Key Recent Facts
- [fact]

## Recent Changes
- Created: [[Page]]
- Updated: [[Page]]

## Active Threads
- [thread]
```

## Log Entry Format

`wiki/log.md` 新条目放在顶部。

MVP 格式：

```markdown
## [2026-06-25] ingest | Source Title
- Source: `.raw/articles/source.md`
- Summary: [[Source Title]]
- Pages created: [[Page A]], [[Page B]]
- Pages updated: [[wiki/index]], [[wiki/hot]]
- Key insight: One sentence.
```

## Index Entry Format

`wiki/index.md` 应按页面类别组织：

```markdown
## Concepts
- [[Concept Name]] — one-line description

## Entities
- [[Entity Name]] — role or relevance

## Sources
- [[Source Title]] — source type and summary

## Questions
- [[Question Title]] — answer summary
```

## 非目标

- MVP 不支持 LYT。
- MVP 不支持 PARA。
- MVP 不支持 Zettelkasten。
- MVP 不做现有 vault 的组织模式迁移。
- MVP 不要求生成 Dataview 或 Bases dashboard。
