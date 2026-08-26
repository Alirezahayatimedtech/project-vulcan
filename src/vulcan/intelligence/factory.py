from __future__ import annotations

from vulcan.intelligence.base import IntelligenceProvider
from vulcan.intelligence.openai_compatible import OpenAICompatibleProvider
from vulcan.intelligence.settings import IntelligenceSettings


def build_provider(settings: IntelligenceSettings) -> IntelligenceProvider:
    if settings.provider == "openai-compatible":
        return OpenAICompatibleProvider(settings)
    raise ValueError(f"Unsupported intelligence provider: {settings.provider}")
