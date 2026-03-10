from pathlib import Path

from typer.testing import CliRunner

from docugen import cli

runner = CliRunner()


def test_cli_fails_with_invalid_path() -> None:
    result = runner.invoke(cli.app, ["not-a-real-path"])

    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_cli_fails_without_api_key(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('x')\n", encoding="utf-8")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("DOCUGEN_CONFIG", raising=False)
    monkeypatch.setenv("DOCUGEN_DOTENV", str(tmp_path / "missing.env"))

    result = runner.invoke(cli.app, [str(tmp_path)])

    assert result.exit_code == 1
    assert "Missing GEMINI_API_KEY" in result.output


def test_cli_happy_path_from_dotenv(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("def main():\n    return 0\n", encoding="utf-8")

    dotenv = tmp_path / ".env"
    dotenv.write_text("GEMINI_API_KEY=dotenv-secret\n", encoding="utf-8")

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("DOCUGEN_CONFIG", raising=False)
    monkeypatch.setenv("DOCUGEN_DOTENV", str(dotenv))

    monkeypatch.setattr(cli, "scan_python_files", lambda _: [project / "main.py"])
    monkeypatch.setattr(
        cli,
        "parse_project",
        lambda _files, _root: {
            "main.py": {
                "classes": [],
                "functions": [],
                "metrics": {"class_count": 0, "method_count": 0, "function_count": 0, "line_count": 1},
                "errors": [],
            }
        },
    )
    monkeypatch.setattr(
        cli,
        "prepare_for_ai",
        lambda _parsed: {
            "summary": {
                "file_count": 1,
                "class_count": 0,
                "method_count": 0,
                "function_count": 0,
                "error_count": 0,
            },
            "files": [],
        },
    )

    class FakeGeminiClient:
        def __init__(self, api_key: str, model: str) -> None:
            self.api_key = api_key
            self.model = model

        def generate_markdown(self, project_metadata, user_prompt=None) -> str:
            assert self.api_key == "dotenv-secret"
            return "## Auto README"

    monkeypatch.setattr(cli, "GeminiClient", FakeGeminiClient)

    result = runner.invoke(cli.app, [str(project), "--output", "README.md", "--prompt", "Keep it short"])

    assert result.exit_code == 0
    readme = project / "README.md"
    assert readme.exists()
    assert "## Auto README" in readme.read_text(encoding="utf-8")
