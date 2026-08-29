from fastapi import FastAPI

from vulcan.core.compiler import IntentCompiler
from vulcan.environment.gate import EnvironmentGate
from vulcan.evolution.engine import VulcanEvolutionEngine
from vulcan.evolution.models import EvolutionRequest, EvolutionResult
from vulcan.generators.manifest import build_application_manifest
from vulcan.models.environment import GroundedForgeRequest, GroundedForgeResult
from vulcan.models.spec import ForgeRequest, ForgeResult
from vulcan.safety.gate import SafetyGate

app = FastAPI(
    title="VULCAN",
    version="0.1.0",
    description="Healthcare systems, forged on demand — research prototype.",
)

compiler = IntentCompiler()
safety_gate = SafetyGate()
environment_gate = EnvironmentGate()
evolution_engine = VulcanEvolutionEngine()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "project": "VULCAN", "stage": "research-prototype"}


@app.post("/forge", response_model=ForgeResult)
def forge(request: ForgeRequest) -> ForgeResult:
    spec = compiler.compile(request.need)
    findings, deployable = safety_gate.evaluate(spec)
    return ForgeResult(
        specification=spec,
        safety_findings=findings,
        deployable=deployable,
    )


@app.post("/forge/grounded", response_model=GroundedForgeResult)
def grounded_forge(request: GroundedForgeRequest) -> GroundedForgeResult:
    readiness = environment_gate.evaluate(request.need, request.environment)
    if not readiness.ready:
        return GroundedForgeResult(
            environment_ready=False,
            readiness=readiness,
            deployable=False,
        )

    spec = compiler.compile(request.need)
    findings, deployable = safety_gate.evaluate(spec)
    return GroundedForgeResult(
        environment_ready=True,
        readiness=readiness,
        specification=spec,
        safety_findings=findings,
        deployable=deployable,
    )


@app.post("/forge/evolve", response_model=EvolutionResult)
def evolve(request: EvolutionRequest) -> EvolutionResult:
    return evolution_engine.evolve(request)


@app.post("/manifest")
def manifest(request: ForgeRequest) -> dict:
    spec = compiler.compile(request.need)
    findings, deployable = safety_gate.evaluate(spec)
    return {
        "manifest": build_application_manifest(spec),
        "safety_findings": [f.model_dump() for f in findings],
        "deployable": deployable,
    }
