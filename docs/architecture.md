# Architecture

Project Vulcan is structured as a constrained healthcare software compiler.

```text
Natural-language healthcare need
        ↓
IntentCompiler
        ↓
SystemSpec
        ↓
Manifest generator
        ↓
SafetyGate
        ↓
Research-only application manifest
```

## Boundary

The prototype does **not** let an LLM directly execute clinical logic. The future LLM layer should only help compile intent into a typed `SystemSpec`. Deterministic modules then validate, generate and gate the workflow.

## ROP proof of concept

The current ROP request is transformed into:

- ophthalmology domain classification;
- FHIR EHR read integration;
- DICOM imaging/PACS read integration;
- gestational age, birth weight and prior encounter data requirements;
- clinician review and follow-up approval points;
- clinical-decision-support risk level;
- static safety findings.

## Safety position

Research-only. No autonomous diagnosis, treatment, EHR write, order creation or patient contact.
