from __future__ import annotations

from pathlib import Path

import typer

from docugen.api.gemini_client import DEFAULT_MODEL, GeminiClient
from docugen.core.parser import parse_project
from docugen.core.processor import prepare_for_ai
from docugen.core.scanner import scan_python_files
from docugen.templates.engine import render_readme
from docugen.utils.config_manager import load_runtime_config
from docugen.utils.logger import get_logger

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Generate technical README files from Python projects.",
)


@app.command()
def generate(
    path: str = typer.Argument(..., help="Path to the Python project to analyze."),
    output: str = typer.Option("README.md", "--output", "-o", help="Output Markdown file name."),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Gemini model name."),
    prompt: str | None = typer.Option(None, "--prompt", "-p", help="Optional additional instruction."),
    config: Path | None = typer.Option(None, "--config", help="Optional TOML config file path."),
) -> None:
    logger = get_logger()
    project_path = Path(path).expanduser().resolve()

    if not project_path.exists() or not project_path.is_dir():
        logger.error(f"Project path does not exist or is not a directory: {project_path}")
        raise typer.Exit(code=1)

    settings = load_runtime_config(
        cli_model=model,
        cli_output=output,
        config_path=config,
    )

    if not settings.api_key:
        logger.error("Missing GEMINI_API_KEY (set it in environment or .env).")
        raise typer.Exit(code=1)

    with logger.status("Scanning Python files..."):
        python_files = scan_python_files(project_path)

    if not python_files:
        logger.warning("No Python files found to analyze.")
        raise typer.Exit(code=1)

    with logger.status("Parsing source files with AST..."):
        parsed_data = parse_project(python_files, project_path)
        processed_data = prepare_for_ai(parsed_data)

    client = GeminiClient(api_key=settings.api_key, model=settings.model)

    with logger.status("Generating markdown with Gemini..."):
        ai_markdown = client.generate_markdown(processed_data, user_prompt=prompt)

    output_path = Path(settings.output)
    if not output_path.is_absolute():
        output_path = project_path / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_markdown = render_readme(
        ai_content=ai_markdown,
        project_name=project_path.name,
        summary=processed_data["summary"],
    )

    output_path.write_text(final_markdown, encoding="utf-8", newline="\n")

    summary = processed_data["summary"]
    logger.success(f"Documentation generated at: {output_path}")
    logger.info(
        "Scanned "
        f"{summary['file_count']} files, "
        f"{summary['class_count']} classes, "
        f"{summary['function_count']} functions, "
        f"{summary['method_count']} methods."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
