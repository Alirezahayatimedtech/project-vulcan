# Research Landscape

Vulcan sits at the intersection of:

- healthcare agents;
- EHR/FHIR task environments;
- natural-language-to-workflow systems;
- software generation;
- clinical decision support safety;
- ROP screening and longitudinal follow-up.

## Adjacent work

- MedAgentBench: realistic FHIR-based medical-agent tasks.
- HealthAdminBench: multi-step healthcare administration workflows.
- HealthAgentBench: interactive healthcare-agent benchmark environments.
- EHRAgent: natural language to executable reasoning over EHR tables.
- AutoFlow: automatic workflow generation for LLM agents.
- THESEUS: natural language to structured specification to executable healthcare analysis.
- AgentClinic / AI Hospital / MedAgents: simulated clinical interaction and multi-agent medical reasoning.

## Design lesson

The safe near-term pattern is:

```text
LLM or parser extracts intent
        ↓
validated specification
        ↓
deterministic compiler/runtime
        ↓
safety gate
        ↓
sandbox validation
```

The prototype therefore avoids unconstrained autonomous clinical action.
