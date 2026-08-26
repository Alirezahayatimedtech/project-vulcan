from __future__ import annotations

import json

from pydantic import ValidationError

from vulcan.core.compiler import IntentCompiler
from vulcan.intelligence.base import IntelligenceError, IntelligenceProvider
from vulcan.intelligence.factory import build_provider
from vulcan.intelligence.settings import IntelligenceSettings
from vulcan.models.spec import (
    AgentRole,
    IntelligenceResult,
    IntelligenceTrace,
    SystemSpec,
)

ROLE_PROMPTS = {
    AgentRole.PLANNER: (
        "Decompose the task into a precise, auditable plan. Preserve constraints and "
        "identify unknowns."
    ),
    AgentRole.RESEARCHER: (
        "Analyze only supplied evidence. Never invent citations or claim external retrieval "
        "you did not perform."
    ),
    AgentRole.ENGINEER: (
        "Design implementable software with explicit interfaces, tests, failure modes, and "
        "minimal hidden assumptions."
    ),
    AgentRole.TESTER: (
        "Try to falsify the proposed system with deterministic tests, edge cases, and "
        "reproducible checks."
    ),
    AgentRole.CRITIC: (
        "Independently identify unsafe assumptions, unsupported claims, security risks, and "
        "missing validation."
    ),
}


class IntelligenceKernel:
    def __init__(
        self,
        settings: IntelligenceSettings | None = None,
        provider: IntelligenceProvider | None = None,
        deterministic_compiler: IntentCompiler | None = None,
    ) -> None:
        self.settings = settings or IntelligenceSettings.from_env()
        self.provider = provider
        if self.provider is None and self.settings.mode != "deterministic":
            self.provider = build_provider(self.settings)
        self.deterministic_compiler = deterministic_compiler or IntentCompiler()

    def compile(self, need: str) -> tuple[SystemSpec, IntelligenceTrace]:
        if self.settings.mode == "deterministic":
            return self._deterministic(need, source="deterministic")
        try:
            spec = self._compile_with_model(need)
            return spec, IntelligenceTrace(
                source="model",
                provider=self.provider.name if self.provider else self.settings.provider,
                model=self.settings.model_for(AgentRole.PLANNER),
                role=AgentRole.PLANNER,
            )
        except (
            IntelligenceError,
            ValidationError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ):
            if self.settings.mode == "model":
                raise
            return self._deterministic(need, source="deterministic-fallback")

    def run(self, role: AgentRole, task: str, context: str | None = None) -> IntelligenceResult:
        if self.provider is None or self.settings.mode == "deterministic":
            raise IntelligenceError("No model provider is enabled")
        model = self.settings.model_for(role)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a component inside VULCAN, a software-generation research system. "
                    + ROLE_PROMPTS[role]
                ),
            },
            {"role": "user", "content": self._task_content(task, context)},
        ]
        output = self.provider.complete(messages, model=model, temperature=0.1, max_tokens=4096)
        return IntelligenceResult(
            role=role,
            output=output,
            provider=self.provider.name,
            model=model,
        )

    def status(self, *, probe: bool = False) -> dict[str, object]:
        status = self.settings.public_dict()
        status["available"] = self.provider.probe() if probe and self.provider else None
        return status

    def _compile_with_model(self, need: str) -> SystemSpec:
        if self.provider is None:
            raise IntelligenceError("No model provider is configured")
        schema = json.dumps(SystemSpec.model_json_schema(), separators=(",", ":"))
        messages = [
            {
                "role": "system",
                "content": (
                    "You are VULCAN's intent compiler. Convert the user's need into exactly one "
                    "JSON object matching the provided SystemSpec JSON schema. Do not add "
                    "markdown. "
                    "Do not decide whether the system is safe or deployable; an independent safety "
                    "gate does that. For clinical decision support, encode explicit clinician "
                    "review steps. Never fabricate evidence, model performance, or regulatory "
                    "approval. Schema: "
                    + schema
                ),
            },
            {"role": "user", "content": need.strip()},
        ]
        raw = self.provider.complete(
            messages,
            model=self.settings.model_for(AgentRole.PLANNER),
            temperature=0.0,
            max_tokens=4096,
            json_mode=True,
        )
        payload = self._parse_json_object(raw)
        spec = SystemSpec.model_validate(payload)
        spec.objective = need.strip()
        spec.human_approval_points = [
            step.name for step in spec.workflow_steps if step.requires_human_approval
        ]
        return spec

    def _deterministic(
        self,
        need: str,
        *,
        source: str,
    ) -> tuple[SystemSpec, IntelligenceTrace]:
        spec = self.deterministic_compiler.compile(need)
        return spec, IntelligenceTrace(
            source=source,
            provider="deterministic",
            model=None,
            role=AgentRole.PLANNER,
        )

    @staticmethod
    def _parse_json_object(raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]).strip()
            if text.startswith("json"):
                text = text[4:].lstrip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start < 0 or end <= start:
                raise
            payload = json.loads(text[start : end + 1])
        if not isinstance(payload, dict):
            raise TypeError("Model output must be a JSON object")
        return payload

    @staticmethod
    def _task_content(task: str, context: str | None) -> str:
        if context:
            return f"Task:\n{task.strip()}\n\nContext:\n{context.strip()}"
        return task.strip()
