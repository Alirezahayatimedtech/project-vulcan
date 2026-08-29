# Architecture

Project VULCAN is a constrained healthcare software compiler with a replaceable intelligence kernel.

```text
Natural-language need
        |
        v
IntelligenceKernel
        |
        +-- role prompt + model router
        |       planner / researcher / engineer / tester / critic
        |
        +-- OpenAI-compatible provider
        |       default: Qwen/Qwen3.8-27B
        |
        +-- deterministic fallback compiler
        |
        v
Typed SystemSpec
        |
        +-- manifest generator
        +-- domain tools/models
        +-- deterministic validators
        |
        v
SafetyGate
        |
        v
Research-only application output
```

## Model boundary

The LLM is a replaceable compiler and reasoning component. It is not the safety authority and it does not directly execute clinical actions.

The model may propose a `SystemSpec`. VULCAN then:

1. validates it against the Pydantic schema;
2. normalizes human-approval points from actual workflow steps;
3. runs the independent `SafetyGate`;
4. blocks high-risk autonomous workflows;
5. exposes the intelligence source in the API result for traceability.

## Provider boundary

`IntelligenceProvider` defines the stable interface between VULCAN and a model server. The first implementation is `OpenAICompatibleProvider`, making local vLLM/SGLang-style endpoints and compatible hosted endpoints interchangeable at the application layer.

The default model is `Qwen/Qwen3.8-27B`. It is configuration, not architecture.

## Roles

The initial roles all use the same provider and model by default:

- planner: task decomposition and formal specification;
- researcher: analysis of supplied evidence without fabricated retrieval;
- engineer: software/interface design;
- tester: falsification and edge-case generation;
- critic: independent risk and assumption review.

`VULCAN_ROLE_MODELS` can override individual role models. The critic can therefore move to a different model without restructuring the system.

## Failure policy

Three intelligence modes are supported:

- `deterministic`: never call a model;
- `auto`: use the model, then fall back to the deterministic compiler on model failure;
- `model`: require the model and return an error if it is unavailable or produces invalid output.

This makes development reproducible while allowing a strict deployment policy later.

## ROP proof of concept

The ROP request can be transformed into:

- ophthalmology domain classification;
- FHIR EHR read integration;
- DICOM imaging/PACS read integration;
- gestational age, birth weight, and prior encounter requirements;
- clinician review and follow-up approval points;
- clinical-decision-support risk level;
- static safety findings.

Domain prediction models remain separate from the LLM. A future ROP classifier or risk model should be called as a validated tool; the LLM should not invent the clinical prediction itself.

## Deployment boundary

The repository ships a Docker image for the VULCAN API. A local Qwen server is a separate process/container so model weights and inference hardware remain independent from the application image.

## Safety position

Research-only. No autonomous diagnosis, treatment, EHR write, order creation, or patient contact.
