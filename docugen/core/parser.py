from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _safe_unparse(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_arguments(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, Any]]:
    args: list[dict[str, Any]] = []
    signature = node.args

    positional = signature.posonlyargs + signature.args
    defaults = [None] * (len(positional) - len(signature.defaults)) + list(signature.defaults)

    for argument, default in zip(positional, defaults):
        args.append(
            {
                "name": argument.arg,
                "annotation": _safe_unparse(argument.annotation),
                "default": _safe_unparse(default),
                "kind": "positional",
            }
        )

    if signature.vararg is not None:
        args.append(
            {
                "name": signature.vararg.arg,
                "annotation": _safe_unparse(signature.vararg.annotation),
                "default": "",
                "kind": "var_positional",
            }
        )

    for argument, default in zip(signature.kwonlyargs, signature.kw_defaults):
        args.append(
            {
                "name": argument.arg,
                "annotation": _safe_unparse(argument.annotation),
                "default": _safe_unparse(default),
                "kind": "keyword_only",
            }
        )

    if signature.kwarg is not None:
        args.append(
            {
                "name": signature.kwarg.arg,
                "annotation": _safe_unparse(signature.kwarg.annotation),
                "default": "",
                "kind": "var_keyword",
            }
        )

    return args


def _extract_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    return {
        "name": node.name,
        "args": _extract_arguments(node),
        "returns": _safe_unparse(node.returns),
        "docstring": ast.get_docstring(node) or "",
        "is_async": isinstance(node, ast.AsyncFunctionDef),
    }


def parse_file(file_path: str | Path, root: str | Path | None = None) -> dict[str, Any]:
    path = Path(file_path).resolve()

    if root is None:
        relative_path = path.name
    else:
        try:
            relative_path = path.relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            relative_path = path.as_posix()

    result: dict[str, Any] = {
        "path": relative_path,
        "classes": [],
        "functions": [],
        "metrics": {
            "line_count": 0,
            "class_count": 0,
            "method_count": 0,
            "function_count": 0,
        },
        "errors": [],
    }

    try:
        source = _read_source(path)
    except OSError as exc:
        result["errors"].append(f"Cannot read file: {exc}")
        return result

    result["metrics"]["line_count"] = len(source.splitlines())

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        message = f"SyntaxError at line {exc.lineno}, column {exc.offset}: {exc.msg}"
        result["errors"].append(message)
        return result

    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [
                _extract_function(child)
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append(
                {
                    "name": node.name,
                    "bases": [_safe_unparse(base) for base in node.bases if _safe_unparse(base)],
                    "docstring": ast.get_docstring(node) or "",
                    "methods": methods,
                }
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(_extract_function(node))

    result["classes"] = classes
    result["functions"] = functions
    result["metrics"]["class_count"] = len(classes)
    result["metrics"]["function_count"] = len(functions)
    result["metrics"]["method_count"] = sum(len(item["methods"]) for item in classes)

    return result


def parse_project(file_paths: list[str | Path], root: str | Path) -> dict[str, dict[str, Any]]:
    root_path = Path(root).resolve()
    parsed: dict[str, dict[str, Any]] = {}

    for file_path in sorted(Path(path).resolve() for path in file_paths):
        record = parse_file(file_path, root_path)
        parsed[record["path"]] = record

    return parsed
