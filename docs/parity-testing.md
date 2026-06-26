# Parity Testing

Parity testing 用来验证不同 Agent adapter 是否产生等效 Wiki 产物。

## 一致性定义

本项目采用 artifact-level equivalence，而不是全量字节级一致。

## 必须稳定的产物

以下产物应尽量字节级稳定：

- transport snapshot schema。
- manifest。
- frontmatter 字段集合。
- log entry 格式。
- index entry 格式。
- lint report schema。
- route / mode 配置。

## 允许表达差异的产物

以下产物允许 LLM 表达差异：

- 来源摘要正文。
- 概念页正文。
- 实体页正文。
- 问题回答正文。
- 比较分析正文。

但这些产物必须满足：

- 页面类型正确。
- frontmatter 合规。
- 来源引用存在。
- wikilink 合规。
- 关键概念被覆盖。
- index / log / hot 被更新。
- lint 通过。

## Fixture 设计

测试应包含小型 fixture vault：

- 一个空 vault。
- 一个已有少量页面的 vault。
- 一个包含 Raw Source 的 vault。
- 一个包含旧 index / log / hot 的 vault。

## 验证方式

测试不应只比较整篇 Markdown 字符串，而应解析并验证：

- 文件树。
- frontmatter。
- Markdown 标题结构。
- wikilink 图。
- 来源引用。
- log entry。
- index entry。
- hot cache 长度和内容主题。

## 失败分类

- Blocker：破坏 Raw Source、漏更新 index/log/hot、生成不可解析 frontmatter。
- High：缺少关键页面、死链、来源引用缺失。
- Medium：页面分类错误、摘要遗漏主要观点。
- Low：措辞差异、标题风格不一致、非关键顺序差异。
