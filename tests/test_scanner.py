from pathlib import Path

from docugen.core.scanner import scan_python_files


def test_scan_python_files_ignores_default_dirs_and_gitignore(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("print('ok')\n", encoding="utf-8")

    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "ignored.py").write_text("print('ignore')\n", encoding="utf-8")

    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("print('ignore')\n", encoding="utf-8")

    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "ignored_dir" / "ignored.py").write_text("print('ignore')\n", encoding="utf-8")

    (tmp_path / "keep.skip.py").write_text("print('ignored by pattern')\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("ignored_dir/\n*.skip.py\n", encoding="utf-8")

    files = scan_python_files(tmp_path)

    discovered = {path.relative_to(tmp_path).as_posix() for path in files}
    assert discovered == {"src/ok.py"}


def test_scan_python_files_from_single_file(tmp_path: Path) -> None:
    file_path = tmp_path / "script.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    files = scan_python_files(file_path)

    assert files == [file_path.resolve()]
