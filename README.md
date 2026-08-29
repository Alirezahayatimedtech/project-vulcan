# VULCAN

**Healthcare systems, forged on demand.**

VULCAN is a research-first prototype for an AI-native healthcare software foundry.

The long-term goal is simple: a clinician or health system describes the capability it needs; VULCAN turns that intent into a formal specification, composes the required workflow and integrations, validates the result, and produces a deployable healthcare workflow or application.

## Core thesis

```text
Clinic facts → EnvironmentSpec
                  +
Clinical or operational need
                  ↓
Intent compiler
                  ↓
Formal healthcare specification
                  ↓
Workflow + agents + integrations + UI manifest
                  ↓
Safety and policy validation
                  ↓
Human approval
                  ↓
Deployment
```

The product is not another chatbot. The product is the **system that can create healthcare software systems**.

## Evidence-grounded environment

VULCAN now has a draft `EnvironmentSpec` for describing the clinic before generating software.
Every environment fact has a provenance status: `verified`, `discovered`, `declared`, `inferred`, `conflicting`, or `unknown`.

`/forge/grounded` fails closed when a required clinic capability is missing, unknown, conflicting, or only inferred. VULCAN therefore does not silently invent EHR, PACS, FHIR, DICOM, or network capabilities.

## Current proof of concept

The first working wedge is **software on demand for ROP screening and follow-up planning**.

The prototype can:

- accept a natural-language healthcare need;
- compile it into a typed `SystemSpec`;
- capture evidence-grounded clinic facts in `EnvironmentSpec`;
- block grounded generation when required environment facts are missing;
- infer ROP/ophthalmology workflow requirements;
- add FHIR and DICOM integration requirements;
- generate a vendor-neutral application manifest;
- run a static safety gate;
- block high-risk autonomous clinical actions;
- expose the process through FastAPI endpoints.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
pytest -q
uvicorn vulcan.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/manifest \
  -H 'Content-Type: application/json' \
  -d @examples/rop_need.json
```

## API

```text
GET  /health
POST /forge
POST /forge/grounded
POST /manifest
```

`/forge` returns the formal `SystemSpec` plus safety findings.

`/forge/grounded` first checks whether the clinic facts required by the requested capability are known and usable. It returns no generated `SystemSpec` when the environment is incomplete.

`/manifest` returns a deployable-style application manifest with data inputs, integrations, workflow steps, UI views, and governance requirements.

## Design principles

1. Facts before generation.
2. Unknown means unknown.
3. Intent in, system out.
4. Interoperability first.
5. Human authority for clinical actions.
6. Traceability and auditability.
7. Replaceable intelligence.
8. Simulation before deployment.
9. Evidence over demo quality.

## Status

Research prototype only. Not a medical device. Not for clinical care. No autonomous diagnosis or treatment is implemented.

## One-line vision

**Ask for a healthcare capability. Receive the system.**
