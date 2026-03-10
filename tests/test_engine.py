from pathlib import Path

from docugen.templates.engine import TemplateEngine, render_readme


def test_render_readme_with_default_template() -> None:
    rendered = render_readme(
        ai_content="## Overview\n\nAuto-generated docs.",
        project_name="demo-project",
        summary={
            "file_count": 2,
            "class_count": 1,
            "function_count": 3,
            "method_count": 4,
            "error_count": 0,
        },
    )

    assert "# demo-project" in rendered
    assert "Auto-generated docs." in rendered
    assert "Python files scanned: 2" in rendered


def test_template_engine_renders_custom_template(tmp_path: Path) -> None:
    template = tmp_path / "custom.j2"
    template.write_text("Hello {{ name }}", encoding="utf-8")

    engine = TemplateEngine(template_dir=tmp_path)
    rendered = engine.render("custom.j2", {"name": "DocuGen"})

    assert rendered == "Hello DocuGen\n"
