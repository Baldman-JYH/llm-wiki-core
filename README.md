# llm-wiki-core

`llm-wiki-core` 是一个面向本地 LLM Wiki 工作流的中性核心项目。它把 [Karpathy 的 LLM Wiki 思想](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 落地为可测试、可维护的 Markdown 知识库工具，让本地智能体能够围绕原始资料持续维护 Wiki，而不是把知识留在一次性对话里。

当前版本为 `v0.1.0-mvp`，已经达到 MVP 本地完成状态：支持 Codex App 与 Codex CLI 的本地使用路径，核心流程通过自动化验证。后续版本会继续扩展 Obsidian CLI、批量摄取、深度检索和更多适配层能力。

## 目录

- [项目定位](#项目定位)
- [主要能力](#主要能力)
- [快速开始](#快速开始)
- [使用方式](#使用方式)
- [命令速查](#命令速查)
- [产物结构](#产物结构)
- [与 claude-obsidian 的关系](#与-claude-obsidian-的关系)
- [文档](#文档)
- [当前边界](#当前边界)
- [路线图](#路线图)
- [开发与测试](#开发与测试)
- [许可证](#许可证)

## 项目定位

LLM Wiki 的核心思想是：人类选择资料和问题方向，LLM 负责阅读、摘要、归档、建立链接、更新索引和发现矛盾，最终形成可长期维护的 Markdown Wiki。

`llm-wiki-core` 关注这套机制中的中性部分：

- 原始资料保存在 `.raw/`，作为只读来源。
- Wiki 内容保存在 `wiki/`，包括索引、日志、近期上下文和知识页面。
- 规则层约束页面结构、frontmatter、wikilink、manifest 和 lint 结果。
- 适配层负责对接 Codex、Claude Code 或其他本地智能体。

## 主要能力

- 初始化标准 LLM Wiki 目录。
- 维护 `.raw/.manifest.json`，记录来源、状态和内容指纹。
- 摄取单个本地 Markdown 来源并生成 Wiki 页面。
- 从 Wiki 页面中检索并回答问题，返回 wikilink 引用。
- 保存长期有价值的结论到 Wiki。
- 通过 `status` 和 `continue` 恢复跨会话上下文。
- 检查 frontmatter、死链、孤立页面和基础结构健康。
- 为 Codex App 与 Codex CLI 生成 `AGENTS.md` 使用入口。
- 使用 `filesystem` 作为当前已实现的运行通道。
- 检测 Obsidian CLI 是否存在，但在其实际读写与搜索能力实现前，不把它作为默认运行通道。

## 快速开始

### 安装

```powershell
git clone https://github.com/Baldman-JYH/llm-wiki-core.git
cd llm-wiki-core
python -m pip install -e .
python -m llm_wiki_core --version
```

如果 `llm-wiki` 命令暂时不在当前 shell 的 `PATH` 中，可以使用等价的模块入口：

```powershell
python -m llm_wiki_core --version
```

### 初始化一个 Wiki

```powershell
llm-wiki init <vault> --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport <vault> --force
```

### 添加并摄取资料

```powershell
New-Item -ItemType Directory -Force <vault>/.raw/articles
Set-Content -Path <vault>/.raw/articles/example.md -Encoding UTF8 -Value "# Example Source`n`nDurable knowledge belongs in the Wiki."
llm-wiki ingest <vault> .raw/articles/example.md
```

### 查询、保存和检查

```powershell
llm-wiki status <vault>
llm-wiki continue <vault>
llm-wiki query <vault> "What does the wiki know about this source?"
llm-wiki save <vault> --title "Saved Insight" --content "Durable insight text."
llm-wiki lint <vault>
```

## 使用方式

### 方式一：直接使用 CLI

适合希望把 `llm-wiki-core` 作为本地命令行工具使用的场景。安装后直接运行 `llm-wiki` 命令即可。

### 方式二：在 Codex App 或 Codex CLI 中使用

先通过 `llm-wiki init` 初始化目标目录。生成的 `AGENTS.md` 会告诉 Codex 如何继续操作这个 Wiki。

常用自然语言触发：

- `set up wiki`
- `check wiki status`
- `resume wiki context`
- `ingest this source`
- `query wiki`
- `save this insight`
- `lint wiki`

### 方式三：使用 Codex 安装脚本

Windows PowerShell：

```powershell
.\integrations\codex\install\install.ps1 -VaultPath <vault> -Purpose "Research local LLM wiki workflows"
.\integrations\codex\install\install.ps1 -VaultPath <vault> -Purpose "Research local LLM wiki workflows" -DryRun
```

macOS / Linux：

```sh
./integrations/codex/install/install.sh <vault> "Research local LLM wiki workflows"
./integrations/codex/install/install.sh --dry-run <vault> "Research local LLM wiki workflows"
```

## 命令速查

| 命令 | 作用 |
|---|---|
| `llm-wiki init <vault> --purpose "..."` | 初始化 Wiki 目录、基础页面和 Codex 入口 |
| `llm-wiki detect-transport <vault> --force` | 检测可用通道并写入快照 |
| `llm-wiki ingest <vault> <source>` | 摄取 `.raw/` 下的单个来源 |
| `llm-wiki status <vault>` | 查看 Wiki 初始化状态、来源数量和运行通道 |
| `llm-wiki continue <vault>` | 读取 `hot`、`index`、`log`，恢复近期上下文 |
| `llm-wiki query <vault> "<question>"` | 从 Wiki 中检索并回答问题 |
| `llm-wiki save <vault> --content "..."` | 保存长期有价值的结论 |
| `llm-wiki lint <vault>` | 检查 Wiki 健康并生成报告 |

## 产物结构

初始化后会在目标目录中生成类似结构：

```text
<vault>/
  AGENTS.md
  .raw/
    .manifest.json
  wiki/
    index.md
    log.md
    hot.md
    overview.md
    sources/
    entities/
    concepts/
    questions/
    comparisons/
    meta/
```

其中：

- `.raw/` 保存原始资料。
- `.raw/.manifest.json` 记录来源状态和指纹。
- `wiki/index.md` 是主索引。
- `wiki/log.md` 是操作日志。
- `wiki/hot.md` 保存近期上下文。
- `wiki/meta/` 保存 lint 报告等元数据。

## 与 claude-obsidian 的关系

[AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) 是 Claude Code + Obsidian 场景下的成熟参考实现。

`llm-wiki-core` 不复制它的全部功能，也不绑定 Claude Code。这个项目抽取其中适合跨本地智能体复用的核心规则，让 Codex App、Codex CLI 和后续适配层都能围绕同一套 Wiki 产物工作。

## 文档

- [用户指南](docs/user-guide.md)
- [发布就绪清单](docs/release-readiness-checklist.md)
- [完成标准](docs/completion-criteria.md)
- [路线图](docs/roadmap.md)
- [路线图排期](docs/roadmap-schedule.md)
- [发布说明](docs/release-notes-v0.1.0-mvp.md)
- [归档说明](docs/archive-manifest.md)
- [MVP 范围](docs/mvp-scope.md)
- [能力映射](docs/capability-mapping.md)
- [操作契约](docs/operation-contract.md)
- [通道契约](docs/transport-contract.md)
- [产物级等价验证](docs/artifact-equivalence-verification.md)

## 当前边界

当前版本聚焦本地 MVP，不包含以下能力：

- 尚未实现 Obsidian CLI 的实际读写与搜索调用。
- 尚未覆盖 `claude-obsidian` 的全部高级能力。
- 尚未实现 URL 摄取、批量摄取、深度检索、向量检索或 LLM 综合写作模式。
- 尚未发布 Codex marketplace plugin。
- 尚未自动修改全局 Codex 配置。
- 尚未接入 MCP 或 REST API 通道。

## 路线图

后续工作分为五个方向：

- R1：增强测试夹具、CLI 输出和错误提示。
- R2：实现并验证 Obsidian CLI 通道。
- R3：扩展 URL 摄取、批量摄取和深度检索。
- R4：完善 Codex 与 Claude Code 适配层。
- R5：增加可选的知识组织模式和高级 lint。

详细安排见 [路线图排期](docs/roadmap-schedule.md)。

## 开发与测试

```powershell
python -m pip install -e .
python -m pytest
```

当前发布线的验证结果记录在 [发布说明](docs/release-notes-v0.1.0-mvp.md) 中。

## 许可证

当前仓库尚未添加许可证文件。正式公开分发前，建议补充明确的 `LICENSE`。
