from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_IGNORED_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    "build",
    "dist",
}


@dataclass(frozen=True)
class GitIgnoreRule:
    pattern: str
    negated: bool
    directory_only: bool
    anchored: bool


def _load_gitignore_rules(root: Path) -> list[GitIgnoreRule]:
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return []

    rules: list[GitIgnoreRule] = []
    for raw_line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        negated = line.startswith("!")
        if negated:
            line = line[1:]

        directory_only = line.endswith("/")
        if directory_only:
            line = line[:-1]

        anchored = line.startswith("/")
        if anchored:
            line = line[1:]

        if line:
            rules.append(
                GitIgnoreRule(
                    pattern=line,
                    negated=negated,
                    directory_only=directory_only,
                    anchored=anchored,
                )
            )

    return rules


def _match_rule(relative_path: str, is_dir: bool, rule: GitIgnoreRule) -> bool:
    normalized = relative_path.replace("\\", "/")

    if rule.anchored:
        path_matches = fnmatch.fnmatch(normalized, rule.pattern)
        subtree_matches = normalized.startswith(rule.pattern + "/")
    elif "/" in rule.pattern:
        path_matches = fnmatch.fnmatch(normalized, rule.pattern)
        subtree_matches = normalized.startswith(rule.pattern + "/")
    else:
        parts = normalized.split("/")
        path_matches = any(fnmatch.fnmatch(part, rule.pattern) for part in parts)
        subtree_matches = any(part == rule.pattern for part in parts)

    matched = path_matches or subtree_matches

    if rule.directory_only:
        return matched and is_dir

    return matched


def _is_ignored(relative_path: str, is_dir: bool, rules: list[GitIgnoreRule]) -> bool:
    ignored = False
    for rule in rules:
        if _match_rule(relative_path, is_dir, rule):
            ignored = not rule.negated
    return ignored


def scan_python_files(root_path: str | Path) -> list[Path]:
    root = Path(root_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if root.is_file():
        return [root] if root.suffix == ".py" else []

    rules = _load_gitignore_rules(root)
    discovered: list[Path] = []

    for current_dir, dirnames, filenames in os.walk(root, topdown=True):
        current = Path(current_dir)

        filtered_dirs: list[str] = []
        for dirname in dirnames:
            if dirname in DEFAULT_IGNORED_DIRS:
                continue

            directory_path = current / dirname
            relative_dir = directory_path.relative_to(root).as_posix()
            if _is_ignored(relative_dir, is_dir=True, rules=rules):
                continue

            filtered_dirs.append(dirname)

        dirnames[:] = filtered_dirs

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            file_path = current / filename
            relative_file = file_path.relative_to(root).as_posix()
            if _is_ignored(relative_file, is_dir=False, rules=rules):
                continue

            discovered.append(file_path.resolve())

    return sorted(discovered)
