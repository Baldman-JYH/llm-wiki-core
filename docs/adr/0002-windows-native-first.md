# ADR 0002: Support Windows Natively

状态：已确认

## 背景

目标用户包括本地 Codex App 与 Codex CLI，覆盖 Windows 与 macOS。

如果 Windows 用户必须安装 WSL 或 Git Bash，安装门槛和失败概率都会提高。

## 决策

Windows 必须原生支持，不依赖 WSL 或 Git Bash。

核心逻辑优先使用 Python。Windows 使用 PowerShell 作为入口包装，macOS / Linux 使用 shell 入口包装。

## 后果

- 现有 POSIX shell 思路不能直接作为唯一实现。
- 路径处理必须覆盖 Windows 路径、空格和非 ASCII 字符。
- 跨平台测试必须覆盖 Windows 默认路径。
- Git Bash / WSL 可以作为高级用户可选路径，但不是默认前提。
