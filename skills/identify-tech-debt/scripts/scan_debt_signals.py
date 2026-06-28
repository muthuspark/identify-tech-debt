#!/usr/bin/env python3
"""Scan a repository for textual technical-debt signals.

This script intentionally reports leads, not final findings. Verify surrounding
code before presenting any result as technical debt.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "bower_components",
    "vendor",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    "target",
    "out",
    "__pycache__",
}

TEXT_EXTENSIONS = {
    ".bash",
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".env",
    ".go",
    ".graphql",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".lua",
    ".md",
    ".mjs",
    ".php",
    ".prisma",
    ".properties",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}

PROSE_EXTENSIONS = {".md", ".rst", ".txt"}

NETWORK_CALLS = re.compile(
    r"\b(fetch|axios\.(get|post|put|patch|delete)|requests\.(get|post|put|patch|delete)|httpx\.(get|post|put|patch|delete)|urllib\.request\.urlopen)\s*\(",
)
DB_CALLS = re.compile(
    r"\b(query|execute|find_many|findMany|find_one|findOne|select|update|insert|delete|save|create)\s*\(|\b(prisma|sequelize|knex|db|repo|repository|client)\.",
    re.IGNORECASE,
)
LOOP_START = re.compile(r"^\s*(for|while)\b|\.forEach\s*\(|\.map\s*\(")
ASYNC_START = re.compile(r"^\s*async\s+(def|function)\b|async\s*\([^)]*\)\s*=>")
BLOCKING_IN_ASYNC = re.compile(
    r"\b(time\.sleep|requests\.(get|post|put|patch|delete)|subprocess\.run|subprocess\.call|execSync|spawnSync|readFileSync|writeFileSync)\s*\(",
)

PATTERNS = [
    (
        "todo-marker",
        "Knowledge",
        "Low",
        re.compile(r"^\s*(#|//|/\*|\*|<!--|--)\s*\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE),
        "Untracked temporary or incomplete work marker.",
    ),
    (
        "hardcoded-secret",
        "Quality",
        "High",
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|password|passwd|private[_-]?key)\b\s*[:=]\s*['\"][^'\"\n]{8,}['\"]"
        ),
        "Potential hardcoded credential or secret-like value.",
    ),
    (
        "broad-exception",
        "Operational",
        "Medium",
        re.compile(r"\bexcept\s+Exception\b|\bexcept\s*:|\bcatch\s*\([^)]*(err|error|e)[^)]*\)"),
        "Broad exception handling can hide distinct failure modes.",
    ),
    (
        "swallowed-exception",
        "Operational",
        "High",
        re.compile(r"\b(pass|return\s+(None|null|false)?|continue)\b"),
        "Exception handler appears to discard failure without surfacing context.",
    ),
    (
        "debug-statement",
        "Operational",
        "Low",
        re.compile(r"\b(console\.log|debugger;|pprint\s*\(|logger\.debug\s*\()"),
        "Debug output may have leaked into production code.",
    ),
    (
        "silent-fallback",
        "Operational",
        "Medium",
        re.compile(r"\bfallback\b|return\s+(None|null|false|\[\]|\{\})\s*(#|//)?\s*$", re.IGNORECASE),
        "Fallback or default behavior may hide a real failure.",
    ),
]


@dataclass
class Finding:
    kind: str
    category: str
    severity: str
    path: str
    line: int
    detail: str
    evidence: str


def is_probably_text(path: Path, max_bytes: int) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        with path.open("rb") as handle:
            chunk = handle.read(min(max_bytes, 4096))
    except OSError:
        return False
    return b"\0" not in chunk


def iter_files(root: Path, max_bytes: int) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".terraform")]
        for filename in filenames:
            path = Path(current) / filename
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            if is_probably_text(path, max_bytes):
                yield path


def relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def line_text(lines: list[str], index: int) -> str:
    return lines[index].strip()[:220]


def add_finding(
    findings: list[Finding],
    root: Path,
    path: Path,
    line_index: int,
    kind: str,
    category: str,
    severity: str,
    detail: str,
    evidence: str,
) -> None:
    findings.append(
        Finding(
            kind=kind,
            category=category,
            severity=severity,
            path=relpath(path, root),
            line=line_index + 1,
            detail=detail,
            evidence=evidence.strip()[:220],
        )
    )


def scan_patterns(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    for index, line in enumerate(lines):
        if "debt-scan: ignore" in line:
            continue
        for kind, category, severity, pattern, detail in PATTERNS:
            if path.suffix.lower() in PROSE_EXTENSIONS and kind not in {"todo-marker", "hardcoded-secret"}:
                continue
            if looks_like_detector_definition(line):
                continue
            if not pattern.search(line):
                continue
            if kind == "swallowed-exception" and not inside_recent_exception(lines, index):
                continue
            if kind == "silent-fallback" and "fallback" not in line.lower() and not inside_recent_exception(lines, index):  # debt-scan: ignore
                continue
            if kind == "hardcoded-secret" and looks_like_placeholder(line):
                continue
            add_finding(findings, root, path, index, kind, category, severity, detail, line_text(lines, index))


def inside_recent_exception(lines: list[str], index: int) -> bool:
    start = max(0, index - 3)
    return any(
        re.match(r"^\s*(except\s*(Exception|BaseException)?\s*(:|as\b)|catch\s*\()", line)
        for line in lines[start : index + 1]
    )


def looks_like_placeholder(line: str) -> bool:
    lowered = line.lower()
    placeholders = ("example", "dummy", "placeholder", "changeme", "replace_me", "your_", "test", "fake")
    return any(token in lowered for token in placeholders)


def looks_like_detector_definition(line: str) -> bool:
    stripped = line.strip()
    if "re.compile(" in stripped or "Pattern.compile(" in stripped:
        return True
    return stripped.startswith(("\"", "'")) and stripped.endswith((",", "),"))


def scan_missing_timeouts(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    for index, line in enumerate(lines):
        if not NETWORK_CALLS.search(line):
            continue
        window = " ".join(lines[index : min(len(lines), index + 4)])
        if "timeout" not in window:
            add_finding(
                findings,
                root,
                path,
                index,
                "missing-timeout",
                "Operational",
                "Medium",
                "Network call does not show an obvious timeout nearby.",
                line_text(lines, index),
            )


def scan_looped_db_calls(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    for index, line in enumerate(lines):
        if not LOOP_START.search(line):
            continue
        window = lines[index + 1 : min(len(lines), index + 16)]
        if any(DB_CALLS.search(candidate) for candidate in window):
            add_finding(
                findings,
                root,
                path,
                index,
                "looped-db-call",
                "Quality",
                "High",
                "Loop contains a database-looking call nearby; investigate possible N+1 behavior.",
                line_text(lines, index),
            )


def scan_async_blocking(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    async_start = None
    for index, line in enumerate(lines):
        if ASYNC_START.search(line):
            async_start = index
        if async_start is not None and index - async_start > 120:
            async_start = None
        if async_start is not None and BLOCKING_IN_ASYNC.search(line):
            add_finding(
                findings,
                root,
                path,
                index,
                "blocking-in-async",
                "Quality",
                "High",
                "Blocking operation appears inside an async function.",
                line_text(lines, index),
            )


def scan_large_python_functions(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    if path.suffix.lower() != ".py":
        return
    starts: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(\s*)def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", line)
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "    "))
        starts.append((index, indent, match.group(2)))
    for offset, (start, indent, name) in enumerate(starts):
        end = len(lines)
        for next_start, next_indent, _ in starts[offset + 1 :]:
            if next_indent <= indent:
                end = next_start
                break
        size = end - start
        if size > 90:
            add_finding(
                findings,
                root,
                path,
                start,
                "large-function",
                "Maintenance",
                "Medium",
                f"Python function '{name}' is {size} lines long.",
                line_text(lines, start),
            )


def scan_duplicate_config_keys(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    if path.suffix.lower() not in {".env", ".ini", ".properties", ".toml", ".yaml", ".yml"}:
        return
    seen: dict[str, int] = {}
    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith(("#", ";", "[")):
            continue
        match = re.match(r"([A-Za-z0-9_.-]+)\s*[:=]", line)
        if not match:
            continue
        key = match.group(1)
        if key in seen:
            add_finding(
                findings,
                root,
                path,
                index,
                "duplicate-config-key",
                "Operational",
                "Medium",
                f"Config key also appears on line {seen[key] + 1}.",
                line_text(lines, index),
            )
        else:
            seen[key] = index


def scan_file_shape(root: Path, path: Path, lines: list[str], findings: list[Finding]) -> None:
    if len(lines) > 1000:
        add_finding(
            findings,
            root,
            path,
            0,
            "large-file",
            "Maintenance",
            "Medium",
            f"File is {len(lines)} lines long.",
            line_text(lines, 0) if lines else "",
        )
    stem = path.stem.lower()
    if stem in {"util", "utils", "helper", "helpers", "common", "shared"} and len(lines) > 500:
        add_finding(
            findings,
            root,
            path,
            0,
            "utility-dumping-ground",
            "Maintenance",
            "Medium",
            "Large generic utility/helper file may be accumulating unrelated responsibilities.",
            line_text(lines, 0) if lines else "",
        )


def collect_duplicate_stems(root: Path, files: list[Path], findings: list[Finding]) -> None:
    by_stem: dict[str, list[Path]] = defaultdict(list)
    ignored = {"index", "main", "test", "tests", "types", "schema", "config"}
    for path in files:
        stem = path.stem.lower()
        if stem in ignored or len(stem) < 4:
            continue
        by_stem[stem].append(path)
    for stem, paths in sorted(by_stem.items()):
        if len(paths) < 4:
            continue
        evidence = ", ".join(relpath(path, root) for path in paths[:6])
        add_finding(
            findings,
            root,
            paths[0],
            0,
            "repeated-file-stem",
            "Duplication",
            "Low",
            f"File stem '{stem}' appears in {len(paths)} files; check for duplicate concepts.",
            evidence,
        )


def scan_repo(root: Path, max_bytes: int) -> list[Finding]:
    findings: list[Finding] = []
    files = list(iter_files(root, max_bytes))
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        scan_patterns(root, path, lines, findings)
        scan_missing_timeouts(root, path, lines, findings)
        scan_looped_db_calls(root, path, lines, findings)
        scan_async_blocking(root, path, lines, findings)
        scan_large_python_functions(root, path, lines, findings)
        scan_duplicate_config_keys(root, path, lines, findings)
        scan_file_shape(root, path, lines, findings)
    collect_duplicate_stems(root, files, findings)
    return findings


def render_markdown(findings: list[Finding], root: Path) -> str:
    counts: dict[str, int] = defaultdict(int)
    for finding in findings:
        counts[finding.kind] += 1
    severity_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    lines = [
        f"# Technical Debt Signal Scan",
        "",
        f"Repository: `{root}`",
        f"Signals: {len(findings)}",
        "",
        "These are heuristic leads. Verify source context before reporting them as debt.",
        "",
    ]
    if counts:
        lines.append("## Summary")
        lines.append("")
        for kind, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {kind}: {count}")
        lines.append("")
    lines.append("## Signals")
    lines.append("")
    for finding in sorted(findings, key=lambda item: (severity_rank.get(item.severity, 9), item.path, item.line)):
        lines.append(
            f"- **{finding.severity}** `{finding.kind}` ({finding.category}) "
            f"`{finding.path}:{finding.line}` - {finding.detail}"
        )
        if finding.evidence:
            lines.append(f"  Evidence: `{finding.evidence}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="Repository or project directory to scan")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    parser.add_argument("--max-file-bytes", type=int, default=1_000_000)
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: repo is not a directory: {root}", file=sys.stderr)
        return 2

    findings = scan_repo(root, args.max_file_bytes)
    if args.format == "json":
        output = json.dumps(
            {
                "repo": str(root),
                "signals": [asdict(finding) for finding in findings],
                "count": len(findings),
            },
            indent=2,
            sort_keys=True,
        )
    else:
        output = render_markdown(findings, root)

    if args.output:
        Path(args.output).write_text(output + ("\n" if not output.endswith("\n") else ""), encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
