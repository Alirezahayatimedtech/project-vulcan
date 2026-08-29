import json

import httpx

from vulcan.intelligence.base import IntelligenceError
from vulcan.intelligence.kernel import IntelligenceKernel
from vulcan.intelligence.openai_compatible import OpenAICompatibleProvider
from vulcan.intelligence.settings import IntelligenceSettings
from vulcan.models.spec import AgentRole


class FakeProvider:
    name = "fake"

    def __init__(self, output: str):
        self.output = output
        self.last_model = None

    def complete(self, messages, *, model, temperature=0.1, max_tokens=4096, json_mode=False):
        self.last_model = model
        return self.output

    def probe(self):
        return True


class FailingProvider:
    name = "failing"

    def complete(self, *args, **kwargs):
        raise IntelligenceError("offline")

    def probe(self):
        return False


def model_spec_json() -> str:
    return json.dumps(
        {
            "name": "VULCAN ROP",
            "objective": "placeholder",
            "clinical_domain": "ophthalmology",
            "actors": ["clinician", "clinical-agent"],
            "data_inputs": [
                {"name": "retinal_image", "source": "PACS", "standard": "DICOM"}
            ],
            "integrations": [
                {"system": "Imaging/PACS", "standard": "DICOM", "direction": "read"}
            ],
            "workflow_steps": [
                {
                    "id": "review",
                    "name": "Clinical review",
                    "actor": "clinician",
                    "action": "Review output",
                    "requires_human_approval": True,
                }
            ],
            "output_artifacts": ["dashboard"],
            "human_approval_points": ["hallucinated point"],
            "risk_level": "clinical_decision_support",
            "audit_required": True,
            "notes": [],
        }
    )


def test_kernel_compiles_with_model_and_normalizes_approval_points():
    settings = IntelligenceSettings(mode="model", role_models={"planner": "planner-model"})
    provider = FakeProvider(model_spec_json())
    kernel = IntelligenceKernel(settings=settings, provider=provider)
    need = "Build an ROP screening system with clinician review."
    spec, trace = kernel.compile(need)
    assert trace.source == "model"
    assert trace.model == "planner-model"
    assert provider.last_model == "planner-model"
    assert spec.objective == need
    assert spec.human_approval_points == ["Clinical review"]


def test_auto_mode_falls_back_when_model_is_unavailable():
    settings = IntelligenceSettings(mode="auto")
    kernel = IntelligenceKernel(settings=settings, provider=FailingProvider())
    spec, trace = kernel.compile("Build an ROP risk screening system with clinician approval.")
    assert spec.clinical_domain == "ophthalmology"
    assert trace.source == "deterministic-fallback"


def test_role_model_router_uses_critic_override():
    settings = IntelligenceSettings(mode="model", role_models={"critic": "independent-critic"})
    provider = FakeProvider("critique")
    kernel = IntelligenceKernel(settings=settings, provider=provider)
    result = kernel.run(AgentRole.CRITIC, "Review this architecture")
    assert result.model == "independent-critic"
    assert provider.last_model == "independent-critic"


def test_openai_compatible_provider_parses_response():
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["model"] == "Qwen/Qwen3.8-27B"
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    settings = IntelligenceSettings(mode="model")
    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleProvider(settings, client=client)
    output = provider.complete(
        [{"role": "user", "content": "test"}],
        model="Qwen/Qwen3.8-27B",
    )
    assert output == "ok"
