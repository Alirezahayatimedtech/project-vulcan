from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from vulcan.models.spec import AgentRole


@dataclass(frozen=True)
class IntelligenceSettings:
    mode: str = "auto"
    provider: str = "openai-compatible"
    model: str = "Qwen/Qwen3.8-27B"
    base_url: str = "http://127.0.0.1:8001/v1"
    api_key: str = "local"
    timeout_seconds: float = 120.0
    role_models: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "IntelligenceSettings":
        mode = os.getenv("VULCAN_INTELLIGENCE_MODE", "auto").strip().lower()
        if mode not in {"auto", "model", "deterministic"}:
            raise ValueError("VULCAN_INTELLIGENCE_MODE must be auto, model, or deterministic")
        raw_role_models = os.getenv("VULCAN_ROLE_MODELS", "{}")
        try:
            role_models = json.loads(raw_role_models)
        except json.JSONDecodeError as exc:
            raise ValueError("VULCAN_ROLE_MODELS must be a JSON object") from exc
        if not isinstance(role_models, dict):
            raise ValueError("VULCAN_ROLE_MODELS must be a JSON object")
        valid_roles = {role.value for role in AgentRole}
        role_models = {
            str(key): str(value)
            for key, value in role_models.items()
            if str(key) in valid_roles and value
        }
        return cls(
            mode=mode,
            provider=os.getenv("VULCAN_MODEL_PROVIDER", "openai-compatible").strip().lower(),
            model=os.getenv("VULCAN_MODEL_NAME", "Qwen/Qwen3.8-27B").strip(),
            base_url=os.getenv("VULCAN_MODEL_BASE_URL", "http://127.0.0.1:8001/v1").rstrip("/"),
            api_key=os.getenv("VULCAN_MODEL_API_KEY", "local"),
            timeout_seconds=float(os.getenv("VULCAN_MODEL_TIMEOUT_SECONDS", "120")),
            role_models=role_models,
        )

    def model_for(self, role: AgentRole) -> str:
        return self.role_models.get(role.value, self.model)

    def public_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "role_models": self.role_models,
        }
