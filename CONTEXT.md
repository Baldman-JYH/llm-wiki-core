# Context

本文件只定义领域词汇，不记录实现决策。

## 领域词汇

**LLM Wiki**

由 LLM 持续维护的 Markdown 知识库。它不是一次性问答结果，而是会随着来源和问题持续增长、修正、链接和沉淀的知识资产。本项目使用的 LLM Wiki 含义以 Karpathy 的 LLM Wiki gist 为 canonical 来源。

**Abstract Pattern**

Karpathy LLM Wiki gist 所描述的高层思想。它定义为什么需要 LLM 维护持久 Wiki，以及 raw sources、wiki、schema、ingest、query、lint、index、log 等核心关系。

**Reference Implementation**

对 Abstract Pattern 的一个已存在、可运行、可观察的具体实现。本项目当前主要参考 `claude-obsidian`，它展示了 Claude Code + Obsidian 下如何实现 LLM Wiki。

**Practice Variant**

基于 Abstract Pattern，并吸收 Reference Implementation 经验后，为某个 Agent 或平台组合设计的实践版本。`llm-wiki-core` 目标是成为 Codex / Claude 等本地 Agent 可共享的中性 Practice Variant。

**Raw Source**

人类提供的原始来源材料，例如文章、转录、PDF 摘要、网页剪藏、会议记录或研究笔记。Raw Source 是事实来源，默认不可被 LLM 修改。

**Wiki**

LLM 维护的综合层，由 Markdown 页面组成，包含来源摘要、概念页、实体页、问题页、比较页、索引、日志和热缓存。

**Schema**

约束 LLM 如何维护 Wiki 的规则层，包括目录结构、frontmatter、wikilink、操作流程、写入规则和验证规则。

**Ingest**

把一个或多个 Raw Source 读入 Wiki 的过程。Ingest 不只是保存摘要，还应更新相关概念、实体、索引、日志和热缓存。

**Query**

基于已有 Wiki 回答问题的过程。Query 应先读热缓存和索引，再读取少量相关页面，最后综合回答。

**Lint**

检查 Wiki 健康度的过程，包括死链、孤页、缺失 frontmatter、过期声明、重复页面、缺失反链和未归档洞见。

**Hot Cache**

保存近期上下文的短文档，用于让后续 Agent 快速恢复最近工作状态。它是缓存，不是完整日志。

**Index**

Wiki 的内容目录。它帮助人类和 LLM 快速找到相关页面。

**Log**

Wiki 的操作时间线。它记录 ingest、query、lint、save 等动作，帮助理解知识库如何演化。

**Agent**

执行 Wiki 维护工作的 LLM 运行体，例如 Codex、Claude Code 或其他本地 coding agent。

**Adapter**

让某个 Agent 运行时接入 LLM Wiki core 的薄层。Adapter 负责命令映射、启动上下文和平台入口，不拥有领域规则。

**Adapter Parity**

不同 Adapter 面向用户提供相同命令语义和知识库维护效果。它不要求不同模型逐字生成相同正文，但要求同一操作维护同一类 Wiki 产物并通过同一验证契约。

**Transport**

读写 Wiki 文件的通道。第一阶段包括 filesystem transport 和可选 Obsidian CLI transport。

**Artifact-Level Equivalence**

不同 Agent 执行同一 Wiki 操作后，产物在结构、文件集合、frontmatter、wikilink、索引、日志、验证结果和知识行为上等效，但不要求所有 LLM 正文逐字相同。

**Deterministic Artifact**

应尽量稳定、可比较、可测试的产物，例如 manifest、frontmatter schema、log entry、index entry、transport snapshot 和 lint report。

**LLM-Authored Content**

由 LLM 综合写出的正文内容，例如来源摘要、概念解释、实体说明、问题回答和比较分析。它应满足结构和验证要求，但不强求逐字一致。
