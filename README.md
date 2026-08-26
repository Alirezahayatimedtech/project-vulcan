# VULCAN

**Healthcare systems, forged on demand.**

VULCAN is a research-first prototype for an AI-native healthcare software foundry.

The long-term goal is simple: a clinician or health system describes the capability it needs; VULCAN turns that intent into a formal specification, composes the required workflow and integrations, validates the result, and produces a deployable healthcare workflow or application.

## Core thesis

```text
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

## Current proof of concept

The first working wedge is **software on demand for ROP screening and follow-up planning**.

The prototype can:

- accept a natural-language healthcare need;
- compile it into a typed `SystemSpec`;
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
POST /manifest
```

`/forge` returns the formal `SystemSpec` plus safety findings.

`/manifest` returns a deployable-style application manifest with data inputs, integrations, workflow steps, UI views, and governance requirements.

## Design principles

1. Intent in, system out.
2. Interoperability first.
3. Human authority for clinical actions.
4. Traceability and auditability.
5. Replaceable intelligence.
6. Simulation before deployment.
7. Evidence over demo quality.

## Status

Research prototype only. Not a medical device. Not for clinical care. No autonomous diagnosis or treatment is implemented.

## One-line vision

**Ask for a healthcare capability. Receive the system.**
