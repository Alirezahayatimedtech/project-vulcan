from __future__ import annotations

import httpx

from vulcan.intelligence.base import IntelligenceError
from vulcan.intelligence.settings import IntelligenceSettings


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(
        self,
        settings: IntelligenceSettings,
        client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings
        timeout = httpx.Timeout(settings.timeout_seconds, connect=2.0)
        self.client = client or httpx.Client(timeout=timeout)

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        payload: dict[str, object] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Content-Type": "application/json"}
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        try:
            response = self.client.post(
                f"{self.settings.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise IntelligenceError(f"Model request failed: {exc}") from exc
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
            return "".join(text_parts).strip()
        raise IntelligenceError("Model response did not contain text content")

    def probe(self) -> bool:
        try:
            response = self.client.get(f"{self.settings.base_url}/models")
            return response.is_success
        except httpx.HTTPError:
            return False
