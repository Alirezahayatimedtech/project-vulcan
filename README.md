# VULCAN

**Healthcare systems, forged on demand.**

VULCAN is a research-first prototype for an AI-native healthcare software foundry. A clinician or health system describes a capability; VULCAN compiles the need into a typed specification, composes a workflow, validates safety constraints, and produces a deployable-style application manifest.

The product is not another chatbot. The product is the **system that can create healthcare software systems**.

## Intelligence architecture

```text
User need
   |
   v
IntelligenceKernel
   |
   +--> Planner
   +--> Researcher
   +--> Engineer
   +--> Tester
   +--> Critic
   |
   v
SystemSpec
   |
   +--> deterministic generators
   +--> domain models/tools
   +--> SafetyGate
   |
   v
Manifest / application
```

The model is replaceable. VULCAN owns the interfaces, state, safety checks, execution, and verification.

### Default core model

The default model is `Qwen/Qwen3.8-27B`, served through an OpenAI-compatible endpoint. The provider interface is model-agnostic, so another local or hosted model can be substituted without changing the rest of VULCAN.

Role-specific models are supported with `VULCAN_ROLE_MODELS`. This makes it possible to keep Qwen as the planner/engineer while using an independent critic later.

## Current proof of concept

The first working wedge is **software on demand for ROP screening and follow-up planning**.

The prototype can:

- accept a natural-language healthcare need;
- use a local model to compile it into a typed `SystemSpec`;
- fall back to a deterministic compiler when the model is unavailable in `auto` mode;
- infer ROP/ophthalmology workflow requirements;
- add FHIR and DICOM integration requirements;
- generate a vendor-neutral application manifest;
- run a safety gate independently of the LLM;
- block high-risk autonomous clinical actions;
- expose planner, researcher, engineer, tester, and critic roles through one kernel;
- route specific roles to different models;
- expose the process through FastAPI endpoints.

## Quick start: deterministic mode

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
export VULCAN_INTELLIGENCE_MODE=deterministic
pytest -q
uvicorn vulcan.api.app:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Run with Qwen3.8-27B

Start an OpenAI-compatible local server. One option is vLLM:

```bash
vllm serve Qwen/Qwen3.8-27B \
  --host 0.0.0.0 \
  --port 8001
```

Then run VULCAN:

```bash
export VULCAN_INTELLIGENCE_MODE=auto
export VULCAN_MODEL_PROVIDER=openai-compatible
export VULCAN_MODEL_NAME=Qwen/Qwen3.8-27B
export VULCAN_MODEL_BASE_URL=http://127.0.0.1:8001/v1
uvicorn vulcan.api.app:app --host 0.0.0.0 --port 8000
```

`auto` uses the model when available and falls back to the deterministic compiler if the model endpoint fails. Set `VULCAN_INTELLIGENCE_MODE=model` to fail closed instead of falling back.

## Multi-model routing

The default is one model for every role. Override selected roles with JSON:

```bash
export VULCAN_ROLE_MODELS='{"critic":"another-model","engineer":"Qwen/Qwen3.8-27B"}'
```

The first architecture therefore stays simple while keeping a clean path to independent verification.

## Docker

Build and run the API:

```bash
docker build -t vulcan .
docker run --rm -p 8000:8000 \
  -e VULCAN_INTELLIGENCE_MODE=auto \
  -e VULCAN_MODEL_BASE_URL=http://host.docker.internal:8001/v1 \
  vulcan
```

`docker-compose.yml` also includes a GPU vLLM service behind the `local-model` profile.

## API

```text
GET  /health
GET  /intelligence/status
POST /intelligence/run
POST /forge
POST /manifest
```

`POST /forge` returns the formal `SystemSpec`, the intelligence source used, and safety findings.

`POST /manifest` returns a deployable-style application manifest with data inputs, integrations, workflow steps, UI views, governance requirements, and intelligence trace.

`POST /intelligence/run` exposes the five initial roles. It does not bypass the safety gate or execute clinical actions.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `VULCAN_INTELLIGENCE_MODE` | `auto` | `auto`, `model`, or `deterministic` |
| `VULCAN_MODEL_PROVIDER` | `openai-compatible` | Provider implementation |
| `VULCAN_MODEL_NAME` | `Qwen/Qwen3.8-27B` | Default core model |
| `VULCAN_MODEL_BASE_URL` | `http://127.0.0.1:8001/v1` | Local/remote compatible endpoint |
| `VULCAN_MODEL_API_KEY` | `local` | Optional endpoint key |
| `VULCAN_MODEL_TIMEOUT_SECONDS` | `120` | Inference timeout |
| `VULCAN_ROLE_MODELS` | `{}` | JSON map of role to model |

## Design principles

1. Intent in, system out.
2. Model-independent architecture.
3. Deterministic tools before free-form generation where possible.
4. Human authority for clinical actions.
5. Traceability and auditability.
6. Independent safety checks.
7. Simulation before deployment.
8. Evidence over demo quality.

## Deployment

Every push and pull request runs tests and static checks. Pushes to `main` also build and publish the API container to GitHub Container Registry through `.github/workflows/container.yml`.

## Status

Research prototype only. Not a medical device. Not for clinical care. No autonomous diagnosis or treatment is implemented.

## One-line vision

**Ask for a healthcare capability. Receive the system.**
