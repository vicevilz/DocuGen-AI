from __future__ import annotations

from typing import Any, Mapping


def _as_clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _normalize_args(args: list[Mapping[str, Any]] | None) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for arg in args or []:
        normalized.append(
            {
                "name": _as_clean_text(arg.get("name", "")),
                "annotation": _as_clean_text(arg.get("annotation", "")),
                "default": _as_clean_text(arg.get("default", "")),
                "kind": _as_clean_text(arg.get("kind", "positional")),
            }
        )
    return normalized


def _normalize_function(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": _as_clean_text(record.get("name", "")),
        "args": _normalize_args(record.get("args", [])),
        "returns": _as_clean_text(record.get("returns", "")),
        "docstring": _as_clean_text(record.get("docstring", "")),
        "is_async": bool(record.get("is_async", False)),
    }


def _normalize_class(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": _as_clean_text(record.get("name", "")),
        "bases": [_as_clean_text(base) for base in record.get("bases", [])],
        "docstring": _as_clean_text(record.get("docstring", "")),
        "methods": [_normalize_function(method) for method in record.get("methods", [])],
    }


def _normalize_metrics(metrics: Mapping[str, Any] | None) -> dict[str, int]:
    metrics = metrics or {}
    return {
        "line_count": int(metrics.get("line_count", 0) or 0),
        "class_count": int(metrics.get("class_count", 0) or 0),
        "method_count": int(metrics.get("method_count", 0) or 0),
        "function_count": int(metrics.get("function_count", 0) or 0),
    }


def prepare_for_ai(parsed_files: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []

    totals = {
        "file_count": 0,
        "class_count": 0,
        "method_count": 0,
        "function_count": 0,
        "error_count": 0,
    }

    for path in sorted(parsed_files.keys()):
        record = parsed_files[path]
        classes = [_normalize_class(item) for item in record.get("classes", [])]
        functions = [_normalize_function(item) for item in record.get("functions", [])]
        metrics = _normalize_metrics(record.get("metrics", {}))
        errors = [_as_clean_text(error) for error in record.get("errors", []) if _as_clean_text(error)]

        files.append(
            {
                "path": path,
                "classes": classes,
                "functions": functions,
                "metrics": metrics,
                "errors": errors,
            }
        )

        totals["file_count"] += 1
        totals["class_count"] += metrics["class_count"]
        totals["method_count"] += metrics["method_count"]
        totals["function_count"] += metrics["function_count"]
        totals["error_count"] += len(errors)

    return {
        "summary": totals,
        "files": files,
    }
