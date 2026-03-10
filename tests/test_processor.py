from docugen.core.processor import prepare_for_ai


def test_prepare_for_ai_normalizes_records_and_summary() -> None:
    parsed = {
        "a.py": {
            "classes": [
                {
                    "name": "A",
                    "bases": [None, "Base"],
                    "docstring": None,
                    "methods": [
                        {
                            "name": "run",
                            "args": [{"name": "x", "annotation": None, "default": None}],
                            "returns": None,
                            "docstring": None,
                            "is_async": False,
                        }
                    ],
                }
            ],
            "functions": [],
            "metrics": {"class_count": 1, "method_count": 1, "function_count": 0},
            "errors": [""],
        },
        "b.py": {
            "classes": [],
            "functions": [
                {
                    "name": "main",
                    "args": [],
                    "returns": "int",
                    "docstring": "entrypoint",
                    "is_async": False,
                }
            ],
            "metrics": {"class_count": 0, "method_count": 0, "function_count": 1},
            "errors": ["oops"],
        },
    }

    prepared = prepare_for_ai(parsed)

    assert prepared["summary"] == {
        "file_count": 2,
        "class_count": 1,
        "method_count": 1,
        "function_count": 1,
        "error_count": 1,
    }

    first = prepared["files"][0]
    assert first["path"] == "a.py"
    assert first["classes"][0]["docstring"] == ""
    assert first["classes"][0]["bases"][0] == ""
    assert first["classes"][0]["methods"][0]["args"][0]["annotation"] == ""
