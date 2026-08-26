from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException, Query

from vulcan.generators.manifest import build_application_manifest
from vulcan.intelligence.base import IntelligenceError
from vulcan.intelligence.kernel import IntelligenceKernel
from vulcan.interoperability.fhir import FHIRSandboxClient, build_rop_screening_bundle
from vulcan.models.spec import (
    ForgeRequest,
    ForgeResult,
    IntelligenceRequest,
    IntelligenceResult,
    ROPForgeRequest,
    ROPForgeResult,
)
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
        "safety_findings": [finding.model_dump() for finding in findings],
        "deployable": deployable,
        "intelligence": trace.model_dump(),
    }


@app.post("/v1/forge/rop", response_model=ROPForgeResult)
def forge_rop(request: ROPForgeRequest) -> ROPForgeResult:
    """Compile one ROP need into a safe, testable FHIR workflow artifact.

    FHIR execution is opt-in and only uses the server configured through FHIR_BASE_URL.
    This endpoint does not accept an arbitrary target URL from the caller.
    """
    try:
        spec, trace = kernel.compile(request.need)
    except (IntelligenceError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    findings, deployable = safety_gate.evaluate(spec)
    bundle = build_rop_screening_bundle(spec, request.case) if deployable else None
    execution = None

    if request.execute_fhir:
        if not deployable or bundle is None:
            raise HTTPException(status_code=409, detail="SafetyGate blocked FHIR execution")
        base_url = os.getenv("FHIR_BASE_URL")
        if not base_url:
            raise HTTPException(status_code=503, detail="FHIR_BASE_URL is not configured")
        try:
            execution = FHIRSandboxClient(base_url).execute_transaction(bundle)
        except (httpx.HTTPError, ValueError) as exc:
            detail = f"FHIR sandbox execution failed: {exc}"
            raise HTTPException(status_code=502, detail=detail) from exc

    return ROPForgeResult(
        specification=spec,
        safety_findings=findings,
        deployable=deployable,
        fhir_bundle=bundle,
        fhir_execution=execution,
        intelligence=trace,
    )
