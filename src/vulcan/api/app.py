from fastapi import FastAPI

from vulcan.core.compiler import IntentCompiler
from vulcan.generators.manifest import build_application_manifest
from vulcan.models.spec import ForgeRequest, ForgeResult
from vulcan.safety.gate import SafetyGate

app = FastAPI(
    title="VULCAN",
    version="0.1.0",
    description="Healthcare systems, forged on demand — research prototype.",
)

compiler = IntentCompiler()
safety_gate = SafetyGate()


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


@app.post("/manifest")
def manifest(request: ForgeRequest) -> dict:
    spec = compiler.compile(request.need)
    findings, deployable = safety_gate.evaluate(spec)
    return {
        "manifest": build_application_manifest(spec),
        "safety_findings": [f.model_dump() for f in findings],
        "deployable": deployable,
    }
