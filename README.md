# VULCAN

**Healthcare systems, forged on demand.**

![Vulcan — from clinic to intelligent clinic](assets/vulcan-classic-clinic.jpg)

VULCAN is a research-first prototype for an AI-native healthcare software foundry.

## Core loop

```text
Collected clinic facts
        ↓
EnvironmentSpec
        ↓
Clinic Ontology
        ↓
User need + trusted components
        ↓
Acceptance tests
        ↓
SafetyGate
        ↓
Generate/evolve software
        ↓
VULCAN ClinicGym
        ↓
Objective verification
        ↓
Silent validation → limited pilot
```

VULCAN does not permit the coding layer to invent missing EHR, PACS, FHIR, DICOM or network capabilities.

## Evidence-grounded environment

Every environment fact has a provenance state: `verified`, `discovered`, `declared`, `inferred`, `conflicting`, or `unknown`.

Required facts that are missing, inferred, conflicting or unsupported block generation. Concrete integration endpoints are required before connector code can be generated.

This environment model is grounded in established interoperability standards rather than vendor assumptions: [IHE Eye Care / Unified Eye Care Workflow](https://wiki.ihe.net/index.php/Unified_Eye_Care_Workflow) for ophthalmic workflow and system actors, [DICOM PS3.2](https://dicom.nema.org/medical/dicom/current/output/chtml/part02/PS3.2.html) for device and PACS conformance capabilities, and [HL7 FHIR CapabilityStatement](https://hl7.org/fhir/R4/capabilitystatement.html) for discoverable EHR/API capabilities. See [`docs/EVIDENCE_BASE.md`](docs/EVIDENCE_BASE.md).

## Software-on-demand foundations

VULCAN now adds four machine-readable layers before deployment:

- **Clinic Ontology** — converts collected facts into clinic objects and relationships.
- **Trusted Component Catalog** — selects reusable FHIR, DICOM, audit and approval building blocks.
- **Acceptance Contract** — defines objective pass/fail tests before candidate software is accepted.
- **Deployment Plan** — enforces `ClinicGym -> silent validation -> limited pilot` with rollback.

These choices are informed by successful patterns from Palantir Ontology, ServiceNow application development/Build Agent, Replit Agent, SWE-bench, MedAgentBench and Waymo simulation. References and implementation mapping are in [`docs/EVIDENCE_BASE.md`](docs/EVIDENCE_BASE.md).

## Autonomous software evolution

`POST /forge/evolve` implements an ERA-inspired software search loop:

`generate -> compile/objectively score -> select -> mutate -> repeat`

Each evolution task is seeded with:

```text
environment.json
clinic_ontology.json
components.json
acceptance_tests.json
deployment_plan.json
```

The search uses rank-based Flat-UCB/PUCT-style exploration. Safety and environment grounding are hard gates, not optimization metrics. Generated Python is syntax-checked without executing arbitrary candidate code in this draft.

Methodological basis: Aygun et al., *Nature* 2026, doi:10.1038/s41586-026-10658-6.

## VULCAN ClinicGym

`clinicgym/` is a synthetic executable ophthalmology clinic used to test generated software before any real deployment.

Current draft includes:

- [HAPI FHIR JPA Server](https://github.com/hapifhir/hapi-fhir-jpaserver-starter) as a fake EHR;
- [Orthanc](https://www.orthanc-server.com/) as a fake PACS/DICOM server;
- a verified synthetic `EnvironmentSpec`;
- an objective verifier;
- normal and fault scenarios including FHIR timeout, PACS outage, wrong patient, malformed DICOM, network interruption and unauthorized write attempts.

The executable healthcare environment follows [MedAgentBench](https://stanfordmlgroup.github.io/projects/medagentbench/); objective software verification follows [SWE-bench](https://github.com/SWE-bench/SWE-bench); multi-system scenario/checkpoint design is informed by [HealthAdminBench](https://arxiv.org/abs/2604.09937) and [WebArena](https://webarena.dev/); extensive failure-scenario simulation is inspired by [Waymo](https://waymo.com/waymo-driver/) as a safety-engineering analogy. Full mapping is in [`clinicgym/README.md`](clinicgym/README.md).

## Current prototype

The prototype can:

- capture an ophthalmology clinic in evidence-grounded `EnvironmentSpec`;
- convert that environment into a machine-readable clinic ontology;
- select trusted reusable healthcare components;
- generate acceptance tests from the requested capability;
- compile a natural-language need into `SystemSpec`;
- block generation when required clinic facts are unavailable;
- evolve candidate applications using objective scores and Flat-UCB search;
- generate FHIR/DICOM connector configuration only from collected facts;
- simulate a minimal EHR/PACS clinic environment for safe testing;
- define staged deployment and rollback requirements;
- preserve the clinical `SafetyGate`.

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
2. Model the clinic before coding.
3. Prefer trusted reusable components over reinvention.
4. Define acceptance tests before accepting software.
5. Simulate before deployment.
6. Objective tests over LLM self-judgement.
7. Safety constraints cannot be traded for score.
8. Human authority for clinical actions.
9. Monitoring and rollback are part of deployment.
10. Evidence over demo quality.

## Status

Research prototype only. Not a medical device. Not for clinical care. No autonomous diagnosis or treatment is implemented.

**Ask for a healthcare capability. Receive the system.**
