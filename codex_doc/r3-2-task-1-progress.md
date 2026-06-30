# R3.2 URL Ingest Task 1 进展

## 阶段 1：补充失败测试

- 已在 `tests/unit/test_ingest_operation.py` 增加 URL metadata/title override 覆盖测试。
- 已增加默认 file ingest 行为不变的回归测试。
- 下一步将运行 focused tests，确认新测试先失败，再实现 `ingest_source(...)` 的扩展参数。

## 阶段 2：实现 ingest 扩展

- 已在 `llm_wiki_core/operations/ingest.py` 扩展 `ingest_source(...)` 签名。
- 已支持 `source_type`、`source_title` 与 `manifest_metadata` 透传。
- 已保持默认 file ingest 路径与行为不变。
- 下一步运行 focused tests，确认新增用例通过且既有用例不回归。

## 阶段 3：验证完成

- 已运行 `python -m pytest tests/unit/test_ingest_operation.py -q`。
- 结果：`12 passed`。
- 当前任务实现可进入提交。
