# VULCAN

**Healthcare systems, forged on demand.**

Project Vulcan explores a simple thesis: instead of manually building every healthcare application, a user describes the capability they need and Vulcan compiles that intent into a typed, safety-checked, executable healthcare workflow.

> **Research prototype only. Not a medical device. Not for clinical care.**

## v0.2 proof of concept: ROP

Vulcan can now demonstrate one end-to-end software-on-demand task for retinopathy of prematurity (ROP):

```text
Natural-language need
    ↓
SystemSpec (strict Pydantic schema)
    ↓
Deterministic SafetyGate
    ↓
ROP workflow + FHIR R4 transaction Bundle
    ↓
HAPI FHIR sandbox
    ↓
Golden evaluation / verifier
```

Example need:

> Generate a screening workflow for Retinopathy of Prematurity for infants born at <30 weeks gestation, including FHIR scheduling and DICOM image routing, with clinician review.

The generated FHIR artifacts are deliberately **proposed/draft**, not autonomous clinical orders.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
export VULCAN_INTELLIGENCE_MODE=deterministic
pytest -q
uvicorn vulcan.api.app:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Interoperability sandbox

The Compose stack runs Vulcan plus HAPI FHIR. The optional `local-model` profile still starts Qwen through vLLM.

```bash
docker compose up --build
python scripts/demo_v02.py
```

Then inspect:

- Vulcan Swagger: `http://localhost:8000/docs`
- HAPI FHIR metadata: `http://localhost:8080/fhir/metadata`

## API

```text
GET  /health
GET  /intelligence/status
POST /intelligence/run
POST /forge
POST /manifest
POST /v1/forge/rop
```

`POST /v1/forge/rop` accepts an ROP software need plus a synthetic patient case. It returns the `SystemSpec`, deterministic safety findings, and—when safe—a FHIR transaction bundle. If `execute_fhir=true`, Vulcan posts the bundle only to the server configured by `FHIR_BASE_URL`.

## SafetyGate

Clinical safety does **not** depend on a second LLM agreeing with the first. Deterministic rules independently block high-risk autonomous behavior.

Current safety evals include requests to:

- autonomously change oxygen/respiratory support;
- discharge an ROP infant without follow-up;
- autonomously diagnose/treat without clinician authority.

Run:

```bash
pytest -q tests/safety_evals
```

## Golden evaluation

Vulcan evaluates generated workflows against expected properties rather than judging prose quality.

```bash
python -m vulcan.evals.golden
```

The current ROP golden set checks interoperability standards, workflow steps, domain assignment, deployability, and required safety interceptions.

## SystemSpec

`SystemSpec` is a strict Pydantic v2 contract. Unknown fields are rejected and the schema is versioned.

```bash
python scripts/export_schema.py
```

Generated schema: `schemas/systemspec.schema.json`.

## Intelligence architecture

Vulcan keeps the intelligence provider replaceable. Deterministic mode is the baseline; model-backed planning can emit the same `SystemSpec`, but execution still passes through the same independent safety and verification layers.

The current provider architecture supports OpenAI-compatible endpoints, including local/open-weight serving where legally and operationally available. No single hosted AI vendor is required by the core workflow.

## Design principles

1. Intent in, system out.
2. Typed specifications before execution.
3. Deterministic policy enforcement for clinical safety.
4. Human authority for clinical actions.
5. Open interoperability standards (FHIR/DICOM).
6. Provider-neutral model architecture.
7. Objective verification and golden evals.
8. Simulation before deployment.

## Demo notebook

See `demo_notebook.ipynb` for a visual walkthrough of need → `SystemSpec` → SafetyGate → FHIR bundle plus a dangerous-prompt interception example.

## Documentation

- `docs/V02.md` — v0.2 technical demo
- `docs/ARCHITECTURE.md` — architecture
- `docs/RESEARCH_LANDSCAPE.md` — related work
- `docs/SAFETY.md` — safety principles
- `docs/ROADMAP.md` — roadmap

## Status

Vulcan currently demonstrates **software/workflow generation**, not ROP diagnosis. It uses synthetic patient data and a test FHIR server. Real-world clinical deployment would require clinical validation, security/privacy engineering, local workflow validation, regulatory assessment, and institutional governance.

## Vision

**Ask for a healthcare capability. Receive the system.**
