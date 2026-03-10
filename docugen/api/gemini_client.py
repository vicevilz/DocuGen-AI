from __future__ import annotations

import json
from typing import Any

try:
    from google import genai
except ImportError:  # pragma: no cover - exercised in runtime environments without dependency
    genai = None  # type: ignore[assignment]

DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
SYSTEM_PROMPT = (
    "Actua como un Technical Writer Senior experto en documentacion de software. "
    "Tu tarea es analizar los metadatos de codigo (clases, funciones, docstrings) que te proporcionare.\n"
    "1. Genera una descripcion tecnica de alto nivel pero facil de entender.\n"
    "2. Crea ejemplos de uso (Usage Examples) basados en las firmas de las funciones.\n"
    "3. Manten un tono profesional, conciso y utiliza formato Markdown limpio.\n"
    "4. Si el codigo carece de docstrings, infiere la utilidad basandote en el nombre de las variables y la logica.\n"
    "5. Responde unicamente con el contenido del Markdown, sin introducciones ni despedidas."
)


class GeminiClient:
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        system_prompt: str = SYSTEM_PROMPT,
        client: Any | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("GEMINI_API_KEY is required.")

        self.model = model
        self.system_prompt = system_prompt
        self.client = client or self._build_client(api_key.strip())

    @staticmethod
    def _build_client(api_key: str) -> Any:
        if genai is None:
            raise RuntimeError("google-genai is not installed. Install dependencies first.")
        return genai.Client(api_key=api_key)

    def _build_content(self, project_metadata: dict[str, Any], user_prompt: str | None = None) -> str:
        metadata_json = json.dumps(project_metadata, ensure_ascii=False, indent=2)
        sections = [
            "Project metadata (JSON):",
            "```json",
            metadata_json,
            "```",
        ]

        if user_prompt and user_prompt.strip():
            sections.extend(["", f"Additional instruction: {user_prompt.strip()}"])

        return "\n".join(sections)

    @staticmethod
    def _extract_text(response: Any) -> str:
        direct_text = getattr(response, "text", None)
        if isinstance(direct_text, str) and direct_text.strip():
            return direct_text.strip()

        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) if content is not None else None
            if not parts:
                continue

            text_parts = [getattr(part, "text", "") for part in parts if getattr(part, "text", None)]
            joined = "".join(text_parts).strip()
            if joined:
                return joined

        raise RuntimeError("Gemini response did not include text content.")

    def generate_markdown(self, project_metadata: dict[str, Any], user_prompt: str | None = None) -> str:
        content = self._build_content(project_metadata, user_prompt=user_prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=content,
                config={"system_instruction": self.system_prompt},
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

        return self._extract_text(response)
