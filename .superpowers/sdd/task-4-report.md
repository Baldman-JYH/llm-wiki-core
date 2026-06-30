## Task 4 Report: Query Integration

### 状态
已完成。按 TDD 流程完成回归测试补充、先行失败验证、再实现，并完成聚焦回归验证。

### 修改文件
- `llm_wiki_core/operations/query.py`
- `tests/unit/test_query_save_operations.py`
- `.superpowers/sdd/task-4-report.md`

### 提交 hash
- `aa1a758`

### RED 命令与失败摘要
- 命令：
  - `python -m pytest tests/unit/test_query_save_operations.py::test_query_delegates_candidate_selection_to_search_wiki -q`
- 失败摘要：
  - 失败原因：`AttributeError: module 'llm_wiki_core.operations.query' has no attribute 'search_wiki'`
  - 说明：`query.py` 当时未导入/暴露 `search_wiki`，符合任务预期的红灯基线。

### GREEN 命令与通过摘要
- 命令：
  - `python -m pytest tests/unit/test_query_save_operations.py::test_query_delegates_candidate_selection_to_search_wiki -q`
  - `python -m pytest tests/unit/test_query_save_operations.py tests/unit/test_artifact_equivalence_verification.py -q`
- 通过摘要：
  - `1 passed`
  - `12 passed in 3.67s`

### 自检结果
- `query.py` 已改为调用检索层：`search_wiki(root, question, limit=3, transport=active_transport)`。
- 当检索无结果时返回 `needs_sources`；有结果时返回 `success` 并带 `cited_pages`。
- 两个新增回归测试（委派检索、索引匹配过滤、检索排序）全部通过，覆盖 `query` 与检索层的交互。
- 既有回归点（`artifact_equivalence`）通过，说明查询能力与保存/状态链路未破坏。

### Concerns
- 无
