# R2 Task 2 进展记录

## 阶段 1：上下文确认

- 时间：2026-06-28
- 任务：实现 `ObsidianCliTransport`，以 fake-runner 方式完成可测试的实际 transport。
- 已确认约束：
  - 仅修改 `llm_wiki_core/transport/obsidian_cli.py`
  - 仅修改 `llm_wiki_core/transport/__init__.py`
  - 仅修改 `tests/unit/test_obsidian_cli_transport.py`
  - 不修改 detection、runtime selector、CLI、docs 或其他任务文件
  - official runtime 仅支持 `obsidian`
  - 必须使用 TDD，先 RED 再 GREEN
  - 测试不得依赖真实 Obsidian 安装
- 已阅读：
  - `.superpowers/sdd/task-2-brief.md`
  - `llm_wiki_core/transport/obsidian_cli.py`
  - `llm_wiki_core/transport/__init__.py`
  - `llm_wiki_core/transport/obsidian_cli_runner.py`
  - `llm_wiki_core/transport/filesystem.py`
  - `tests/unit/test_obsidian_cli_transport.py`
  - `tests/unit/test_obsidian_cli_command_profile.py`
- 当前判断：
  - runner/profile 已提供 CLI argv 构造能力
  - transport 仅需补齐路径归一化、runner 调用、错误映射、search 结果解析
  - `__init__.py` 需要同步导出新的错误类型

## 阶段 2：TDD RED

- 已替换 `tests/unit/test_obsidian_cli_transport.py`
  - 使用 `FakeRunner`
  - 覆盖 `read_text` / `write_text` / `append_text`
  - 覆盖 `exists`
  - 覆盖 `list_markdown`
  - 覆盖 `search_text`
  - 覆盖越界路径拒绝
  - 覆盖非零退出错误映射
- RED 命令：
  - `python -m pytest tests/unit/test_obsidian_cli_transport.py -q`
- RED 结果：
  - 6 个测试失败，符合预期
  - 主要失败原因为：
    - `ObsidianCliTransport.__init__()` 仍不接受 `executable` / `vault_selector` / `runner`
    - `ObsidianCliCommandError` 尚未实现
    - 现有 transport 仍为 contract-only stub

## 阶段 3：实现 transport

- 已将 `llm_wiki_core/transport/obsidian_cli.py` 从 contract-only stub 替换为实际实现
- 已新增错误类型：
  - `ObsidianCliTransportError`
  - `ObsidianCliCommandError`
  - `ObsidianCliTimeoutError`
  - `ObsidianCliParseError`
- 已实现能力：
  - 通过 `ObsidianCliProfile` 生成 official `obsidian` CLI 参数
  - 通过注入式 `runner` 执行命令，支持 fake-runner 测试
  - 统一处理非零退出与超时
  - 复用 filesystem transport 的 vault-relative 路径安全约束
  - 解析 `search:context` 输出为 `SearchResult`
  - `exists()` 对常见 not found / missing / no such 场景返回 `False`
- 已更新 `llm_wiki_core/transport/__init__.py` 导出新 transport 错误类型

## 阶段 4：TDD GREEN

- GREEN 命令：
  - `python -m pytest tests/unit/test_obsidian_cli_transport.py tests/unit/test_obsidian_cli_command_profile.py -q`
- GREEN 结果：
  - `9 passed in 0.85s`
- 自检结论：
  - 未引入真实 Obsidian 依赖
  - 仍仅支持 official `obsidian` runtime candidate
  - 未修改 detection、runtime selector、CLI、其他任务文件
