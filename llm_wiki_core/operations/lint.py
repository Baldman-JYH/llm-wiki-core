from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re

from llm_wiki_core.transport.runtime import select_runtime_transport


SEVERITIES = ("blocker", "high", "medium", "low")
REQUIRED_FRONTMATTER_FIELDS = ("type", "title", "created", "updated", "status")


@dataclass(frozen=True)
class LintFinding:
    severity: str
    check: str
    path: str
    message: str


@dataclass(frozen=True)
class LintResult:
    operation: str
    status: str
    findings: list[LintFinding] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    report_path: str | None = None


def lint_wiki(vault_root: str | Path, write_report: bool = True, transport: object | None = None) -> LintResult:
    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    findings: list[LintFinding] = []

    _check_required_paths(active_transport, findings)
    _check_manifest(active_transport, findings)
    pages = active_transport.list_markdown("wiki")  # type: ignore[attr-defined]
    _check_frontmatter(active_transport, pages, findings)
    _check_wikilinks(active_transport, pages, findings)
    _check_orphans(active_transport, pages, findings)

    counts = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        counts[finding.severity] += 1

    report_path = None
    if write_report:
        report_path = _write_report(active_transport, findings, counts)

    status = "success" if counts["blocker"] == 0 else "issues"
    return LintResult(
        operation="lint",
        status=status,
        findings=findings,
        counts=counts,
        report_path=report_path,
    )


def _check_required_paths(transport: object, findings: list[LintFinding]) -> None:
    required = [
        ".raw/.manifest.json",
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md",
        "wiki/overview.md",
        "wiki/sources",
        "wiki/entities",
        "wiki/concepts",
        "wiki/questions",
        "wiki/comparisons",
        "wiki/meta",
    ]
    for relative in required:
        if not transport.exists(relative):  # type: ignore[attr-defined]
            findings.append(LintFinding("blocker", "required-path", relative, "Required path is missing."))


def _check_manifest(transport: object, findings: list[LintFinding]) -> None:
    path = ".raw/.manifest.json"
    if not transport.exists(path):  # type: ignore[attr-defined]
        return
    try:
        manifest = json.loads(transport.read_text(path))  # type: ignore[attr-defined]
    except json.JSONDecodeError as error:
        findings.append(LintFinding("blocker", "manifest-json", ".raw/.manifest.json", f"Manifest is not valid JSON: {error.msg}."))
        return
    if manifest.get("schema_version") != 1:
        findings.append(LintFinding("blocker", "manifest-schema", ".raw/.manifest.json", "Manifest schema_version must be 1."))
    if not isinstance(manifest.get("sources"), dict):
        findings.append(LintFinding("blocker", "manifest-sources", ".raw/.manifest.json", "Manifest sources must be an object."))


def _check_frontmatter(transport: object, pages: list[str], findings: list[LintFinding]) -> None:
    for page in pages:
        text = transport.read_text(page)  # type: ignore[attr-defined]
        frontmatter = _parse_frontmatter(text)
        if frontmatter is None:
            findings.append(LintFinding("high", "frontmatter", page, "Markdown page is missing YAML frontmatter."))
            continue
        if frontmatter == "malformed":
            findings.append(LintFinding("high", "frontmatter", page, "Markdown page frontmatter is missing a closing delimiter."))
            continue
        for field_name in REQUIRED_FRONTMATTER_FIELDS:
            if not frontmatter.get(field_name):
                findings.append(
                    LintFinding(
                        "high",
                        "frontmatter-field",
                        page,
                        f"Frontmatter missing required field: {field_name}.",
                    )
                )


def _check_wikilinks(transport: object, pages: list[str], findings: list[LintFinding]) -> None:
    page_targets = _page_link_targets(transport, pages)
    known_titles = {target for targets in page_targets.values() for target in targets}
    for page in pages:
        text = transport.read_text(page)  # type: ignore[attr-defined]
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            target = link.split("|", 1)[0].split("#", 1)[0].strip()
            if target and target not in known_titles:
                findings.append(
                    LintFinding(
                        "high",
                        "dead-wikilink",
                        page,
                        f"Dead wikilink: [[{target}]].",
                    )
                )


def _check_orphans(transport: object, pages: list[str], findings: list[LintFinding]) -> None:
    page_targets = _page_link_targets(transport, pages)
    referenced: set[str] = set()
    for page in pages:
        text = transport.read_text(page)  # type: ignore[attr-defined]
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            referenced.add(link.split("|", 1)[0].split("#", 1)[0].strip())

    for page in pages:
        if _is_exempt_from_orphan_check(page):
            continue
        if page_targets[page].isdisjoint(referenced):
            findings.append(LintFinding("medium", "orphan-page", page, "Page is not linked from any other page."))


def _is_exempt_from_orphan_check(page: str) -> bool:
    if Path(page).name == "_index.md":
        return True
    return page.endswith(("wiki/index.md", "wiki/log.md", "wiki/hot.md", "wiki/overview.md"))


def _page_link_targets(transport: object, pages: list[str]) -> dict[str, set[str]]:
    page_targets: dict[str, set[str]] = {}
    for page in pages:
        targets = {Path(page).stem}
        title = _frontmatter_title(transport.read_text(page))  # type: ignore[attr-defined]
        if title:
            targets.add(title)
        page_targets[page] = targets
    return page_targets


def _frontmatter_title(text: str) -> str | None:
    frontmatter = _parse_frontmatter(text)
    if not isinstance(frontmatter, dict):
        return None

    title = frontmatter.get("title", "").strip()
    if len(title) >= 2 and title[0] == title[-1] and title[0] in {"'", '"'}:
        title = title[1:-1].strip()
    return title or None


def _parse_frontmatter(text: str) -> dict[str, str] | str | None:
    if not text.startswith("---\n"):
        return None

    end = text.find("\n---", 4)
    if end == -1:
        return "malformed"

    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            continue
        fields[key] = value.strip()
    return fields


def _write_report(transport: object, findings: list[LintFinding], counts: dict[str, int]) -> str:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    date = timestamp[:10]
    relative = f"wiki/meta/lint-report-{date}.md"

    lines = [
        "---",
        "type: meta",
        f'title: "Lint Report {date}"',
        f"created: {date}",
        f"updated: {timestamp}",
        "status: report",
        "---",
        "",
        f"# Lint Report {date}",
        "",
        "## Summary",
        f"- blocker: {counts['blocker']}",
        f"- high: {counts['high']}",
        f"- medium: {counts['medium']}",
        f"- low: {counts['low']}",
        "",
        "## Findings",
    ]
    if findings:
        for finding in findings:
            lines.append(f"- {finding.severity} | {finding.check} | `{finding.path}` | {finding.message}")
    else:
        lines.append("- No findings.")

    return transport.write_text(relative, "\n".join(lines) + "\n")  # type: ignore[attr-defined]
