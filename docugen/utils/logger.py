from __future__ import annotations

from rich.console import Console


class DocuGenLogger:
    def __init__(self) -> None:
        self.console = Console()

    def info(self, message: str) -> None:
        self.console.print(f"[cyan]INFO[/] {message}")

    def warning(self, message: str) -> None:
        self.console.print(f"[yellow]WARN[/] {message}")

    def error(self, message: str) -> None:
        self.console.print(f"[red]ERROR[/] {message}")

    def success(self, message: str) -> None:
        self.console.print(f"[green]OK[/] {message}")

    def status(self, message: str):
        return self.console.status(message, spinner="dots")


def get_logger() -> DocuGenLogger:
    return DocuGenLogger()
