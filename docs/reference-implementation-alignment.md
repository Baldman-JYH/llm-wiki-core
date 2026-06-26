# Reference Implementation Alignment

本文件定义 `llm-wiki-core` 如何理解和对齐 `claude-obsidian`。

## 三层关系

1. **Karpathy LLM Wiki gist** 是 abstract pattern。
2. **`claude-obsidian`** 是 Claude Code + Obsidian 场景下的 reference implementation。
3. **`llm-wiki-core`** 是计划中的中性 practice variant，用来让 Codex App / CLI 等本地 Agent 获得同等核心效果。

## 对齐目标

`llm-wiki-core` 不复制 `claude-obsidian` 的目录历史和 Claude 专属集成，但应对齐它已经验证有效的核心体验：

- `/wiki`：setup、scaffold、continue。
- `ingest [source]`：摄取来源，更新 source / entity / concept 页面。
- `query`：从 hot cache、index 和相关页面综合回答。
- `lint the wiki`：检查孤页、死链、缺失 frontmatter、陈旧声明和结构缺口。
- `/save`：把有价值的对话沉淀为 Wiki 页面。
- `hot.md`：跨会话近期上下文。
- `index.md`：内容目录。
- `log.md`：操作时间线。
- transport fallback：当前以 filesystem 作为已实现 runtime transport；Obsidian CLI 可检测、可记录，actual read/write/search 实现完成后再成为可选增强通道。

## 不直接复制的内容

以下内容可以参考，但不应无条件进入 MVP：

- Claude Code plugin manifest。
- Claude Code slash command 实现细节。
- Claude hooks。
- Claude subagent 编排。
- bash-only 安装和检测脚本。
- DragonScale 高级记忆机制。
- hybrid retrieval。
- autoresearch。
- canvas。
- release blog 工作流。

## Codex 等效标准

Codex adapter 达标时，用户应能在 Codex App / CLI 中完成与 Claude Code 使用 `claude-obsidian` 相同的核心工作：

1. 打开或创建一个 LLM Wiki vault。
2. 放入 raw source。
3. 要求 ingest。
4. 看到 Wiki 页面、index、log、hot 被维护。
5. 向 Wiki 提问并得到引用 Wiki 页面的回答。
6. 要求 lint 并得到可操作的健康检查。
7. 保存有价值的对话结果。

等效标准是 artifact-level equivalence，不是逐字节输出一致。

## 设计边界

`llm-wiki-core` 应保持对 Karpathy abstract pattern 的忠诚：工具是辅助 LLM 维护 Wiki 的手段，不应把系统变成复杂的通用应用平台。
