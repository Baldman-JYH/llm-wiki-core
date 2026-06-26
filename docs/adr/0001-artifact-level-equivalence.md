# ADR 0001: Use Artifact-Level Equivalence

状态：已确认

## 背景

项目目标是让不同本地 Agent adapter，例如 Codex 和 Claude，能够维护同一个 LLM Wiki，并产生一致的用户体验。

一种选择是要求所有产物字节级一致。另一种选择是要求结构、文件、链接、元数据、验证结果和知识行为一致。

Karpathy LLM Wiki pattern 强调的是持久、复利、可维护的 Wiki，而不是逐字复刻的文本。

## 决策

采用 artifact-level equivalence。

确定性产物应尽量字节级稳定；LLM-authored content 不要求逐字一致，但必须通过结构、链接、来源、索引、日志、热缓存和 lint 验证。

## 后果

- 测试需要解析 Markdown 和 frontmatter，而不是只做全文 diff。
- Agent 可以保留综合和表达能力。
- 用户体验聚焦在知识库是否被正确维护。
- 少量机器可读文件仍可使用字节级比较。
