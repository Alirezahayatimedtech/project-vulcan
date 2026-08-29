# VULCAN

**Healthcare systems, forged on demand.**

VULCAN is a research-first prototype for an AI-native healthcare software foundry.

## Core loop

```text
Collected clinic facts -> EnvironmentSpec
                           +
                       User need
                           ↓
                 EnvironmentGate
                           ↓
                    SystemSpec
                           ↓
                     SafetyGate
                           ↓
          Generate candidate software
                           ↓
             Objective evaluation
                           ↓
          Flat-UCB/PUCT-style search
                           ↓
                 Best candidate
```

VULCAN does not permit the coding layer to invent missing EHR, PACS, FHIR, DICOM or network capabilities.

## Evidence-grounded environment

Every environment fact has a provenance state: `verified`, `discovered`, `declared`, `inferred`, `conflicting`, or `unknown`.

Required facts that are missing, inferred, conflicting or unsupported block generation. Concrete integration endpoints are required before connector code can be generated.

## Autonomous software evolution

`POST /forge/evolve` implements an ERA-inspired software search loop:

`generate -> compile/objectively score -> select -> mutate -> repeat`

The search uses rank-based Flat-UCB/PUCT-style exploration. Safety and environment grounding are hard gates, not optimization metrics. Generated Python is syntax-checked without executing arbitrary candidate code in this draft.

Methodological basis: Aygun et al., *Nature* 2026, doi:10.1038/s41586-026-10658-6. See [`docs/EVIDENCE_BASE.md`](docs/EVIDENCE_BASE.md).

## Current prototype

The prototype can:

- compile a natural-language healthcare need into `SystemSpec`;
- capture an ophthalmology clinic in evidence-grounded `EnvironmentSpec`;
- block generation when required clinic facts are unavailable;
- generate candidate application files through specialized coding roles;
- evolve candidates using objective scores and Flat-UCB search;
- generate FHIR/DICOM connector configuration only from collected facts;
- preserve the existing static clinical `SafetyGate`;
- expose the workflow through FastAPI.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
pytest -q
uvicorn vulcan.api.app:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## API

```text
GET  /health
POST /forge
POST /forge/grounded
POST /forge/evolve
POST /manifest
```

## Design principles

1. Facts before generation.
2. Unknown means unknown.
3. Objective tests over LLM self-judgement.
4. Safety constraints cannot be traded for score.
5. Interoperability first.
6. Human authority for clinical actions.
7. Traceability and auditability.
8. Evidence over demo quality.

## Status

Research prototype only. Not a medical device. Not for clinical care. No autonomous diagnosis or treatment is implemented.

**Ask for a healthcare capability. Receive the system.**
