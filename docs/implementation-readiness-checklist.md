# Implementation Readiness Checklist

本文件定义从规划阶段进入实现阶段前必须满足的检查项。

当前阶段仍不写功能代码。

## Readiness Goal

进入实现阶段前，必须确认：

- 实现不会偏离 Karpathy LLM Wiki pattern。
- 实现不会把 `claude-obsidian` 的 Claude 专属机制误放进 core。
- MVP 范围足够小，可以验证 raw sources / wiki / schema 的核心闭环。
- Windows 原生路径明确。
- Codex App / CLI 使用路径明确。

## Required Planning Docs

进入实现前，以下文档必须存在并已审阅：

| 文档 | 作用 |
|---|---|
| `README.md` | 项目定位与 canonical source。 |
| `CONTEXT.md` | 领域词汇。 |
| `docs/mvp-scope.md` | MVP 范围。 |
| `docs/capability-mapping.md` | `claude-obsidian` 能力映射。 |
| `docs/reference-implementation-alignment.md` | 与 `claude-obsidian` 的对齐关系。 |
| `docs/agent-behavioral-contract.md` | 跨 Agent 行为契约。 |
| `docs/manifest-schema.md` | Manifest schema。 |
| `docs/generic-mode-structure.md` | Generic mode 结构。 |
| `docs/codex-command-contract.md` | Codex 入口契约。 |
| `docs/operation-contract.md` | Core operation 契约。 |
| `docs/transport-contract.md` | Transport 契约。 |
| `docs/parity-testing.md` | 等效验证原则。 |
| `docs/test-fixture-plan.md` | 测试夹具计划。 |
| `docs/adapter-packaging-plan.md` | Codex adapter 包装计划。 |

## Decision Checklist

以下决策必须保持确认状态：

- Karpathy gist 是 canonical source。
- `claude-obsidian` 是 reference implementation。
- `llm-wiki-core` 是中性 practice variant。
- MVP 采用 artifact-level equivalence。
- Windows 原生优先，不依赖 WSL / Git Bash。
- Filesystem transport 必需。
- Obsidian CLI transport 可选优先。
- MCP / REST API 延后。
- MVP 接受最小 `.raw/.manifest.json`。
- MVP 只支持 generic organization mode。
- Codex adapter 采用自然语言触发 + slash command 目标体验。

## Implementation Gate

开始写功能代码前，必须由用户明确确认：

```text
开始创建项目骨架和 MVP 实现代码
```

没有这个确认，只能继续修改规划文档。

## First Implementation Slice

若用户确认进入实现，第一片应只创建项目骨架和测试夹具目录，不实现完整业务逻辑。

建议第一片：

- Python package skeleton。
- `tests/fixtures/` skeleton。
- README 文档索引。
- 不实现 ingest/query/lint 逻辑。

## Blockers

以下情况应阻止进入实现：

- 用户认为文档仍未符合 Karpathy LLM Wiki pattern。
- 用户认为 `claude-obsidian` 能力映射有明显错误。
- 用户要求继续修改 MVP 范围。
- Codex App / CLI 的入口策略仍未被接受。
- Windows 原生支持被重新打开讨论。

## Non-Goals

- 本清单不是测试计划。
- 本清单不是代码架构。
- 本清单不授权开始实现。
