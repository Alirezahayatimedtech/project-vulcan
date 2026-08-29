from fastapi import FastAPI, HTTPException, Query

from vulcan.generators.manifest import build_application_manifest
from vulcan.intelligence.base import IntelligenceError
from vulcan.intelligence.kernel import IntelligenceKernel
from vulcan.models.spec import ForgeRequest, ForgeResult, IntelligenceRequest, IntelligenceResult
from vulcan.safety.gate import SafetyGate

app = FastAPI(
    title="VULCAN",
    version="0.2.0",
    description="Healthcare systems, forged on demand — research prototype.",
)

kernel = IntelligenceKernel()
safety_gate = SafetyGate()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "project": "VULCAN",
        "stage": "research-prototype",
        "intelligence": kernel.status(probe=False),
    }


@app.get("/intelligence/status")
def intelligence_status(probe: bool = Query(default=False)) -> dict:
    return kernel.status(probe=probe)


@app.post("/intelligence/run", response_model=IntelligenceResult)
def run_intelligence(request: IntelligenceRequest) -> IntelligenceResult:
    try:
        return kernel.run(request.role, request.task, request.context)
    except IntelligenceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/forge", response_model=ForgeResult)
def forge(request: ForgeRequest) -> ForgeResult:
    try:
        spec, trace = kernel.compile(request.need)
    except (IntelligenceError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    findings, deployable = safety_gate.evaluate(spec)
    return ForgeResult(
        specification=spec,
        safety_findings=findings,
        deployable=deployable,
        intelligence=trace,
    )


@app.post("/manifest")
def manifest(request: ForgeRequest) -> dict:
    try:
        spec, trace = kernel.compile(request.need)
    except (IntelligenceError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    findings, deployable = safety_gate.evaluate(spec)
    return {
        "manifest": build_application_manifest(spec),
        "safety_findings": [f.model_dump() for f in findings],
        "deployable": deployable,
        "intelligence": trace.model_dump(),
    }
