# Test Fixture Plan

本文件定义 MVP parity tests 所需的 fixture vault 计划。

当前阶段只定义测试设计，不创建测试代码。

## 测试目标

测试应验证不同 Adapter 执行同一核心操作后，产生 artifact-level equivalent 的 Wiki 产物。

测试不追求所有 LLM-authored content 字节级一致。

## Fixture Principles

- Fixture 必须小。
- Fixture 必须可读。
- Fixture 必须覆盖 Karpathy LLM Wiki pattern 的核心闭环。
- Fixture 不依赖网络。
- Fixture 不依赖 Obsidian GUI。
- Fixture 不依赖 WSL 或 Git Bash。
- Fixture 应能在 Windows 和 macOS 运行。

## Fixture Set

### F0 Empty Directory

目的：验证 `init`。

结构：

```text
fixtures/f0-empty/
```

预期：

- init 后出现 `.raw/` 和 `wiki/`。
- required pages 存在。
- manifest 存在且合法。

### F1 Fresh Vault

目的：验证 `status`、`continue` 和基础 lint。

结构：

```text
fixtures/f1-fresh-vault/
├── .raw/
│   └── .manifest.json
└── wiki/
    ├── index.md
    ├── log.md
    ├── hot.md
    └── overview.md
```

预期：

- status 能识别已初始化。
- continue 读取 hot / index / log。
- lint 不报告 blocker。

### F2 Single Raw Source

目的：验证 `ingest`。

结构：

```text
fixtures/f2-single-source/
├── .raw/
│   ├── .manifest.json
│   └── articles/
│       └── karpathy-llm-wiki.md
└── wiki/
    ├── index.md
    ├── log.md
    ├── hot.md
    └── overview.md
```

Raw Source 内容应是短小、可公开、可离线的 LLM Wiki pattern 摘要，不直接依赖远端抓取。

预期：

- ingest 后创建 source summary。
- 至少更新 index/log/hot。
- manifest 记录 source。
- 可选创建明显 concept/entity。

### F3 Existing Knowledge

目的：验证 `query` 和 `save`。

结构：

```text
fixtures/f3-existing-knowledge/
├── .raw/
│   └── .manifest.json
└── wiki/
    ├── index.md
    ├── log.md
    ├── hot.md
    ├── sources/
    ├── concepts/
    └── entities/
```

预期：

- query 按 hot -> index -> pages 顺序回答。
- query 默认不修改 Wiki。
- save 可创建 question 或 concept 页面。

### F4 Broken Wiki

目的：验证 `lint`。

结构包括：

- 缺失 frontmatter 的页面。
- dead wikilink。
- orphan page。
- manifest 中指向不存在 source。
- hot cache 过长或缺失 updated。

预期：

- lint 分类报告 blocker/high/medium/low。
- lint 不自动修复。

## Artifact-Level Assertions

测试应解析并验证：

- 文件树。
- manifest JSON。
- YAML frontmatter。
- Markdown 标题结构。
- Wikilinks。
- Index sections。
- Log entries。
- Hot cache sections。

## Byte-Level Assertions

以下产物可以使用更严格比较：

- manifest schema shape。
- transport snapshot schema shape。
- log entry prefix format。
- frontmatter required fields。
- lint report section names。

## Non-Byte Assertions

以下产物不应强行全文 diff：

- source summary 正文。
- concept / entity 正文。
- query answer 正文。
- save 生成的综合内容。

应验证：

- 是否覆盖关键概念。
- 是否引用 Wiki 页面。
- 是否维护 index/log/hot。
- 是否通过 lint。

## Adapter Parity Matrix

MVP 至少规划以下矩阵：

| Operation | Core fixture | Codex adapter | Claude adapter |
|---|---|---|---|
| init | F0 | 必测 | 后续 |
| status | F1 | 必测 | 后续 |
| continue | F1 | 必测 | 后续 |
| ingest | F2 | 必测 | 后续 |
| query | F3 | 必测 | 后续 |
| lint | F4 | 必测 | 后续 |
| save | F3 | 必测 | 后续 |
| detect-transport | F1 | 必测 | 后续 |

Claude adapter parity 可以在 Codex MVP 后补充；MVP 的首要目标是 Codex App / CLI 本地路径。

## Test Data Rules

- 不使用私密材料。
- 不依赖远端 URL。
- 不把完整 Karpathy gist 固定进测试，除非许可和引用边界明确。
- 可以使用短摘要作为 fixture source。

## 非目标

- 本文件不创建测试代码。
- 本文件不定义具体测试框架。
- 本文件不要求真实 Obsidian GUI。
- 本文件不要求真实 Claude Code。
