# ADR 0005: Treat Karpathy LLM Wiki Gist as Canonical

状态：已确认

## 背景

工作区中存在本地文件 `D:/ai/llmWiki/llm-wiki.md`，它用于当前设计讨论和快速阅读。

但是本项目的思想来源不是该本地文件本身，而是 Karpathy 发布的 LLM Wiki gist：

<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

该 gist 将 LLM Wiki 描述为一种抽象 pattern：LLM 逐步构建和维护持久、互联的 Markdown Wiki，使知识随着来源和问题持续复利，而不是每次 query 都从 raw documents 重新检索和拼接。

## 决策

Karpathy LLM Wiki gist 是 `llm-wiki-core` 的 canonical 思想来源。

本地 `D:/ai/llmWiki/llm-wiki.md` 只作为当前工作区内的参考副本。若本地副本与 Karpathy gist 存在差异，应以 Karpathy gist 为准。

## 后果

- README 必须明确说明 canonical source。
- 后续规划、文档和实现决策应优先校准 Karpathy gist，而不是某个本地派生副本。
- `claude-obsidian` 仍可作为参考实现，但不能覆盖 canonical pattern。
- 项目可以根据本地 Codex App / CLI 的目标做实现取舍，但不能偏离 raw sources / wiki / schema、持久复利、LLM 维护 bookkeeping、人类负责来源与问题这些核心思想。
