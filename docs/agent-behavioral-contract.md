# Agent Behavioral Contract

本文件定义不同 Agent adapter 必须遵守的共同行为。它不是某个 Agent 的提示词，而是跨运行时的一致性契约。

## 最高原则

Agent 必须遵守 Karpathy LLM Wiki pattern 的思想：Wiki 是持久、复利、可维护的知识资产，聊天只是接口。

本地 `D:/ai/llmWiki/llm-wiki.md` 可作为工作副本参考；若它与 Karpathy gist 存在差异，应以 Karpathy gist 为准。

`claude-obsidian` 是当前最重要的参考实现。Agent 行为应尽量复现它的核心知识库维护效果，但不能把 Claude Code 专属机制写成 core 的必需前提。

## 启动行为

当 Agent 进入一个 LLM Wiki vault 时，应按顺序读取：

1. 项目级指令文件。
2. Wiki schema。
3. `wiki/hot.md`。
4. `wiki/index.md`。

Agent 不应在没有必要时扫描整个 Wiki。

## Ingest 行为

Agent 执行 ingest 时必须：

- 读取目标 Raw Source。
- 不修改 Raw Source。
- 创建或更新来源摘要页面。
- 创建或更新相关概念页和实体页。
- 更新 `wiki/index.md`。
- 更新 `wiki/log.md`。
- 更新 `wiki/hot.md`。
- 标记明显矛盾、缺口或不确定性。

## Query 行为

Agent 执行 query 时必须：

- 先读取 `wiki/hot.md`。
- 再读取 `wiki/index.md`。
- 只读取必要的相关页面。
- 在回答中引用 Wiki 页面。
- 当回答具有长期价值时，建议保存为问题页或综合页。

## Lint 行为

Agent 执行 lint 时应检查：

- frontmatter 是否完整。
- wikilink 是否存在死链。
- 页面是否孤立。
- 重要概念是否缺页。
- 索引是否缺失新页面。
- 日志是否缺失关键操作。
- 热缓存是否过期或过长。

## Save 行为

Agent 执行 save 时必须区分：

- 聊天中的临时内容。
- 应沉淀进 Wiki 的长期知识。
- 应进入日志的操作记录。

## Manifest 行为

Agent 执行 ingest 时应维护最小 `.raw/.manifest.json`：

- 记录已摄取来源。
- 记录来源与生成页面之间的关系。
- 避免在没有用户明确要求时重复摄取同一来源。

Manifest 是状态记录，不是 Raw Source 内容的替代品。

## 组织模式

MVP 只要求 generic organization mode。Agent 不应在第一阶段默认要求用户选择 LYT、PARA 或 Zettelkasten。

后续 methodology modes 可以作为可选扩展，但不能改变 Karpathy LLM Wiki pattern 的核心关系。

## 一致性要求

不同 Agent adapter 的输出不要求逐字相同，但必须满足 artifact-level equivalence：

- 文件集合一致或可解释。
- 页面类型一致。
- frontmatter 合规。
- wikilink 合规。
- index / log / hot 被正确更新。
- lint 结果可通过。

## 与 claude-obsidian 的体验对齐

Codex adapter 应让用户获得与 Claude Code 使用 `claude-obsidian` 相同的核心体验：

- 用户可以请求 setup / scaffold / continue。
- 用户可以摄取本地来源。
- 用户可以基于 Wiki 提问。
- 用户可以要求 lint。
- 用户可以保存有价值的对话。
- Agent 会维护 hot cache、index、log 和相关页面。

如果某个 Claude Code 专属功能无法在 Codex 中一比一实现，应通过 adapter 提供等价命令语义，而不是改变 core 的领域规则。

Codex adapter 的入口采用双层策略：自然语言触发必须可用，slash command 作为目标体验对齐。

## 禁止行为

- 不得修改 Raw Source。
- 不得把聊天记录当作最终产物。
- 不得跳过 index / log / hot 的维护。
- 不得把某个 Agent 运行时的能力写成 core 的必需前提。
