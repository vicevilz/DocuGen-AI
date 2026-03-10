from pathlib import Path

from docugen.core.parser import parse_file


def test_parse_file_extracts_classes_functions_and_docstrings(tmp_path: Path) -> None:
    code = '''
class User(BaseModel):
    """Represents an application user."""

    def save(self, force: bool = False) -> None:
        """Persist user data."""
        return None


def main(config: dict[str, str]) -> int:
    """Application entrypoint."""
    return 0


async def sync(name: str) -> str:
    return name
'''
    sample = tmp_path / "sample.py"
    sample.write_text(code, encoding="utf-8")

    parsed = parse_file(sample, tmp_path)

    assert parsed["path"] == "sample.py"
    assert parsed["metrics"]["class_count"] == 1
    assert parsed["metrics"]["function_count"] == 2
    assert parsed["metrics"]["method_count"] == 1
    assert parsed["errors"] == []

    class_record = parsed["classes"][0]
    assert class_record["name"] == "User"
    assert class_record["docstring"] == "Represents an application user."
    assert class_record["methods"][0]["name"] == "save"

    function_names = [item["name"] for item in parsed["functions"]]
    assert function_names == ["main", "sync"]


def test_parse_file_handles_syntax_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def broken(:\n    pass\n", encoding="utf-8")

    parsed = parse_file(bad, tmp_path)

    assert parsed["classes"] == []
    assert parsed["functions"] == []
    assert parsed["metrics"]["function_count"] == 0
    assert parsed["errors"]
    assert "SyntaxError" in parsed["errors"][0]
