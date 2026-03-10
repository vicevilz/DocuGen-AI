from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

DEFAULT_TEMPLATE = "default_readme.md.j2"


class TemplateEngine:
    def __init__(self, template_dir: str | Path | None = None) -> None:
        base_dir = Path(template_dir) if template_dir else Path(__file__).resolve().parent
        self.environment = Environment(
            loader=FileSystemLoader(str(base_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        template = self.environment.get_template(template_name)
        rendered = template.render(**context).strip()
        return f"{rendered}\n"


def render_readme(ai_content: str, project_name: str, summary: dict[str, Any] | None = None) -> str:
    engine = TemplateEngine()
    return engine.render(
        DEFAULT_TEMPLATE,
        {
            "project_name": project_name,
            "ai_content": ai_content.strip(),
            "summary": summary or {},
        },
    )
