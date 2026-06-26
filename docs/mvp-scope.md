# MVP Scope

## 目标

第一阶段 MVP 的目标是建立一个符合 Karpathy LLM Wiki pattern 的本地 LLM Wiki core，并能被本地 Codex App 与 Codex CLI 使用。

本地 `D:/ai/llmWiki/llm-wiki.md` 可作为工作副本参考；若它与 Karpathy gist 存在差异，应以 Karpathy gist 为准。

`D:/ai/llmWiki/claude-obsidian` 是重要参考实现。MVP 不复制它的全部能力，但应复现其核心闭环：用户放入来源、Agent 维护 Wiki、查询从 Wiki 中综合、lint 保持健康、hot / index / log 维持跨会话记忆。

MVP 必须证明以下闭环：

1. 人类把来源放入 Raw Source 层。
2. Agent 按 Schema 读取来源并维护 Wiki。
3. Wiki 产生可持续维护的索引、日志、热缓存和页面。
4. Agent 后续查询时基于 Wiki，而不是每次从零检索来源。

## 必须支持

- 初始化基础 Wiki 结构。
- 使用本地文件系统读写 Markdown。
- 检测 Obsidian CLI，并记录其 availability / implementation 状态。
- 在 Obsidian CLI actual read/write/search 实现前，运行时读写搜索使用文件系统。
- 维护 `wiki/index.md`。
- 维护 `wiki/log.md`。
- 维护 `wiki/hot.md`。
- 维护最小 `.raw/.manifest.json`，用于记录已 ingest 的来源。
- 支持单个本地 Raw Source 的基础 ingest。
- 支持基础 query 工作流。
- 支持基础 lint 工作流。
- 支持与 `claude-obsidian` 核心命令语义对齐的 Codex 使用路径。
- 支持 Codex App 与 Codex CLI 的本地使用路径。
- Windows 原生支持。
- macOS 本地支持。

## 暂不支持

- MCP transport。
- REST API transport。
- 远端 Web / Remote Codex 优先路径。
- URL 自动抓取。
- 自动研究循环。
- 多 Agent 并发写入的高级场景。
- 图形界面。
- 复杂语义检索。
- 对所有 LLM 生成正文做字节级黄金文件冻结。

## MVP 命令语义

MVP 阶段先定义命令语义，不强制绑定具体 slash command 实现。

- `init`：创建基础 Raw Source / Wiki / Schema 文件结构。
- `ingest`：把本地来源摄取进 Wiki。
- `query`：从 Wiki 中回答问题。
- `lint`：检查 Wiki 结构健康。
- `save`：把有价值的对话或结论保存为 Wiki 页面。
- `detect-transport`：检测 filesystem / Obsidian CLI 可用性。
- `status`：报告当前 vault 状态和 runtime transport。
- `continue`：读取 hot / index / log 以恢复跨会话上下文。

## MVP 组织模式

MVP 只支持 generic organization mode。

LYT、PARA、Zettelkasten 等 methodology modes 作为后续能力延后。MVP 文档和实现可以保留这些术语的扩展空间，但不得让它们成为第一阶段使用前提。

## Codex 入口策略

MVP 采用双层入口策略：

- 自然语言触发必须可用，例如“set up wiki”“ingest this source”“lint the wiki”。
- slash command 是目标体验，用于对齐 Claude Code 使用 `claude-obsidian` 的体验。

如果 Codex App 与 Codex CLI 对 slash command 的支持存在差异，应优先保证自然语言触发 + skill 能完成同等核心工作。

## 与 claude-obsidian 的 MVP 对齐范围

MVP 应优先对齐以下能力：

- `/wiki` 的 scaffold / continue 语义。
- `ingest [source]` 的单来源摄取语义。
- `query` / `what do you know about X` 的 Wiki-based answer 语义。
- `lint the wiki` 的健康检查语义。
- `/save` 的会话沉淀语义。
- `hot.md`、`index.md`、`log.md` 的维护语义。

MVP 暂不要求对齐以下高级能力：

- `autoresearch`。
- `canvas`。
- `wiki-retrieve` 混合检索。
- `wiki-fold` / DragonScale。
- 多方法论模式的完整迁移。
- Claude Code 专属 hooks 和 plugin 分发体验。

## 验收标准

- 在没有 Obsidian CLI 的机器上，MVP 仍然可用。
- 在有 Obsidian CLI 的机器上，MVP 可记录其 available 状态，但 actual read/write/search 实现前 runtime 仍使用 filesystem。
- Windows 用户不需要 WSL 或 Git Bash。
- 同一 fixture 输入在不同 Agent adapter 下产生 artifact-level equivalent 的 Wiki 产物。
- 生成的 Wiki 能被 Obsidian 打开和浏览。
