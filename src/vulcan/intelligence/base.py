from __future__ import annotations

from typing import Protocol


class IntelligenceError(RuntimeError):
    pass


class IntelligenceProvider(Protocol):
    name: str

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str: ...

    def probe(self) -> bool: ...
