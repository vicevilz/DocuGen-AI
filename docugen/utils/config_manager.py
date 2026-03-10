from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docugen.api.gemini_client import DEFAULT_MODEL


@dataclass(frozen=True)
class RuntimeConfig:
    api_key: str
    model: str
    output: str


def _read_preferences(config_path: Path) -> dict[str, Any]:
    if not config_path.exists() or not config_path.is_file():
        return {}

    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}

    nested = raw.get("docugen")
    if isinstance(nested, dict):
        merged = dict(raw)
        merged.update(nested)
        return merged

    return raw


def _candidate_paths(explicit_config: Path | None) -> list[Path]:
    if explicit_config is not None:
        return [explicit_config.expanduser().resolve()]

    candidates: list[Path] = []
    env_path = os.getenv("DOCUGEN_CONFIG")
    if env_path:
        candidates.append(Path(env_path).expanduser().resolve())

    candidates.append((Path.cwd() / ".docugen.toml").resolve())
    candidates.append((Path.home() / ".config" / "docugen" / "config.toml").resolve())
    candidates.append((Path.home() / ".docugen.toml").resolve())

    deduped: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        marker = str(candidate)
        if marker not in seen:
            deduped.append(candidate)
            seen.add(marker)

    return deduped


def _parse_dotenv(dotenv_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not dotenv_path.exists() or not dotenv_path.is_file():
        return values

    for raw_line in dotenv_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
            value = value[1:-1]

        if key:
            values[key] = value

    return values


def _candidate_dotenv_paths() -> list[Path]:
    explicit = os.getenv("DOCUGEN_DOTENV")
    if explicit:
        return [Path(explicit).expanduser().resolve()]

    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        (Path.cwd() / ".env").resolve(),
        (project_root / ".env").resolve(),
    ]

    deduped: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        marker = str(candidate)
        if marker not in seen:
            deduped.append(candidate)
            seen.add(marker)

    return deduped


def _resolve_api_key() -> str:
    from_env = os.getenv("GEMINI_API_KEY", "").strip()
    if from_env:
        return from_env

    for dotenv_path in _candidate_dotenv_paths():
        dotenv_values = _parse_dotenv(dotenv_path)
        value = dotenv_values.get("GEMINI_API_KEY", "").strip()
        if value:
            return value

    return ""


def load_runtime_config(
    cli_model: str | None,
    cli_output: str | None,
    config_path: Path | None = None,
) -> RuntimeConfig:
    preferences: dict[str, Any] = {}

    for candidate in _candidate_paths(config_path):
        try:
            loaded = _read_preferences(candidate)
        except (OSError, tomllib.TOMLDecodeError):
            loaded = {}
        if loaded:
            preferences.update(loaded)

    api_key = _resolve_api_key()
    model = (cli_model or "").strip() or str(preferences.get("model", DEFAULT_MODEL))
    output = (cli_output or "").strip() or str(preferences.get("output", "README.md"))

    return RuntimeConfig(api_key=api_key, model=model, output=output)
