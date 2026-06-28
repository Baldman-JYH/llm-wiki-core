# R2 Task 3 进展记录

## 阶段 1：上下文确认

- 时间：2026-06-28
- 任务：扩展 `detect_transport` snapshot schema，并为 official `obsidian` 增加 capability probe。
- 已确认约束：
  - 只修改 `llm_wiki_core/operations/detect_transport.py`
  - 只修改 `tests/unit/test_transport_detection.py`
  - 不修改 runtime selector、CLI、docs 或其他任务文件
  - 不回退其他人的改动
  - 不依赖真实 Obsidian 安装或运行
  - official `obsidian` 是唯一 R2 runtime candidate
  - legacy `obsidian-cli` 仅记录为 legacy/unimplemented metadata
  - capability probe 失败后 `preferred` 必须保持 `filesystem`
  - 必须使用 TDD，先 RED 再 GREEN
- 已阅读：
  - `.superpowers/sdd/task-3-brief.md`
  - `llm_wiki_core/operations/detect_transport.py`
  - `tests/unit/test_transport_detection.py`
  - `llm_wiki_core/transport/obsidian_cli.py`
  - `llm_wiki_core/transport/obsidian_cli_runner.py`
- 当前实现判断：
  - 现有 detection 仍把 `obsidian-cli` / `obsidian` 混成一个可执行探测入口
  - snapshot 尚未包含 `capabilities`、`vault_selector`、`transport_kind`
  - `detect_transport()` 尚未支持注入 fake `runner` / `which`
  - official `obsidian` 是否可作为 runtime 候选，还缺 vault 绑定与读写/搜索能力探测

## 阶段 2：TDD RED

- 已更新 `tests/unit/test_transport_detection.py`
  - 新增 official `obsidian` probe 失败场景
  - 新增 official `obsidian` probe 全通过场景
  - 新增 legacy `obsidian-cli` metadata 场景
  - 调整原有 `obsidian-cli` 测试为 legacy 断言
  - 补充 snapshot JSON 对 `transport_kind` 的断言
- RED 命令：
  - `python -m pytest tests/unit/test_transport_detection.py -q`
- RED 结果：
  - `5 failed, 3 passed`
  - 失败原因符合预期：
    - `detect_transport()` 尚未支持 `runner`
    - `detect_transport()` 尚未支持 `which`
    - snapshot JSON 尚未输出 `transport_kind`

## 阶段 3：实现 detect transport 扩展

- 已修改 `llm_wiki_core/operations/detect_transport.py`
  - 为 `TransportAvailability` 增加：
    - `capabilities`
    - `vault_selector`
    - `transport_kind`
  - 为 `detect_transport()` 增加 `runner` 与 `which` 注入点，便于 fake-runner 测试
  - 将 official `obsidian` 与 legacy `obsidian-cli` 分开建模
  - 为 official `obsidian` 增加 capability probe：
    - `read`
    - `write`
    - `append`
    - `list`
    - `search`
  - probe 使用 `.vault-meta/obsidian-cli-probe.md`，并在结束时清理
  - 仅当 official `obsidian` 全部 probe 通过时，才把 `preferred` 设为 `obsidian`
  - 若 probe 失败，则继续保持 `preferred = filesystem`
  - 扩展 snapshot JSON 的序列化与反序列化，保证新字段可 round-trip

## 阶段 4：TDD GREEN

- GREEN 命令：
  - `python -m pytest tests/unit/test_transport_detection.py -q`
- GREEN 结果：
  - `8 passed in 0.65s`
- 当前自检：
  - 未依赖真实 Obsidian 安装
  - 未修改 runtime selector、CLI、docs 或其他任务文件
  - legacy `obsidian-cli` 仅作为 metadata 记录
  - official `obsidian` 只有在 capability probe 全通过时才会成为 `preferred`
