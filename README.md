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
              VULCAN ClinicGym
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

This environment model is grounded in established interoperability standards rather than vendor assumptions: [IHE Eye Care / Unified Eye Care Workflow](https://wiki.ihe.net/index.php/Unified_Eye_Care_Workflow) for ophthalmic workflow and system actors, [DICOM PS3.2](https://dicom.nema.org/medical/dicom/current/output/chtml/part02/PS3.2.html) for device and PACS conformance capabilities, and [HL7 FHIR CapabilityStatement](https://hl7.org/fhir/R4/capabilitystatement.html) for discoverable EHR/API capabilities. See [`docs/EVIDENCE_BASE.md`](docs/EVIDENCE_BASE.md).

## Autonomous software evolution

`POST /forge/evolve` implements an ERA-inspired software search loop:

`generate -> compile/objectively score -> select -> mutate -> repeat`

The search uses rank-based Flat-UCB/PUCT-style exploration. Safety and environment grounding are hard gates, not optimization metrics. Generated Python is syntax-checked without executing arbitrary candidate code in this draft.

Methodological basis: Aygun et al., *Nature* 2026, doi:10.1038/s41586-026-10658-6. See [`docs/EVIDENCE_BASE.md`](docs/EVIDENCE_BASE.md).

## VULCAN ClinicGym

`clinicgym/` is a synthetic executable ophthalmology clinic used to test generated software before any real deployment.

Current draft includes:

- HAPI FHIR as a fake EHR;
- Orthanc as a fake PACS/DICOM server;
- a verified synthetic `EnvironmentSpec`;
- an objective verifier for app startup, FHIR retrieval, PACS retrieval, environment-contract compliance, unauthorized writes, and required output.

The design follows the executable-environment + objective-verifier pattern used by MedAgentBench and SWE-bench. See [`clinicgym/README.md`](clinicgym/README.md).

## Current prototype

The prototype can:

- compile a natural-language healthcare need into `SystemSpec`;
- capture an ophthalmology clinic in evidence-grounded `EnvironmentSpec`;
- block generation when required clinic facts are unavailable;
- generate candidate application files through specialized coding roles;
- evolve candidates using objective scores and Flat-UCB search;
- generate FHIR/DICOM connector configuration only from collected facts;
- simulate a minimal EHR/PACS clinic environment for safe testing;
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

ClinicGym:

```bash
docker compose -f clinicgym/docker-compose.yml up
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
3. Simulate before deployment.
4. Objective tests over LLM self-judgement.
5. Safety constraints cannot be traded for score.
6. Interoperability first.
7. Human authority for clinical actions.
8. Traceability and auditability.
9. Evidence over demo quality.

## Status

Research prototype only. Not a medical device. Not for clinical care. No autonomous diagnosis or treatment is implemented.

**Ask for a healthcare capability. Receive the system.**
