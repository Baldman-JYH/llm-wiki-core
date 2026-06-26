# ADR 0003: Create a Neutral Core Project

状态：已确认

## 背景

当前参考项目 `claude-obsidian` 面向 Claude Code 设计，并且其远端仓库不是用户仓库。

新的目标是构建基于 LLM Wiki pattern 的多 Agent 本地 Wiki 系统，优先支持 Codex App 与 CLI，同时保留未来适配 Claude、OpenCode、Gemini 等运行时的空间。

`claude-obsidian` 不是 abstract pattern 本身，而是该 pattern 的具体实践案例。它已经验证了 `/wiki`、ingest、query、lint、save、hot cache、index、log、Obsidian CLI transport、methodology modes 等一组有效体验。

## 决策

新项目采用中性核心方向，暂定名为 `llm-wiki-core`。

`claude-obsidian` 作为 reference implementation、上游来源或 Claude adapter 的素材，不作为未来主品牌。

`llm-wiki-core` 的目标不是削弱 `claude-obsidian` 的实践效果，而是把其中可跨 Agent 复用的核心抽象出来，让 Codex adapter 能实现相同的知识库维护效果。

## 后果

- 新项目可以围绕跨 Agent 与跨平台需求重新组织。
- Claude 与 Codex 都作为 adapter 接入 core。
- 后续不应直接在 `claude-obsidian` main 上做大规模重构。
- 需要后续建立 `claude-obsidian` capability mapping，明确哪些能力进入 MVP，哪些作为后续 adapter 或高级模块。
