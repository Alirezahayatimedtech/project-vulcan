# VULCAN Evidence Base

VULCAN should generate software from collected facts and objective tests, not unsupported model assumptions.

## 1. Clinic environment grounding

- IHE Eye Care / Unified Eye Care Workflow: models ophthalmic EHR, PACS, acquisition devices, worklists and workflow actors.  
  https://wiki.ihe.net/index.php/Unified_Eye_Care_Workflow
- DICOM PS3.2 Conformance: use manufacturer conformance statements to establish actual device and PACS capabilities.  
  https://dicom.nema.org/medical/dicom/current/output/html/part02.html
- HL7 FHIR CapabilityStatement: interrogate actual EHR/FHIR capabilities through the server capability statement rather than inferring them from vendor identity.  
  https://hl7.org/fhir/R4/capabilitystatement.html

Implementation: `EnvironmentSpec` + `EnvironmentGate`.

## 2. Autonomous software search

Aygun E, Belyaeva A, Comanici G, et al. **An AI system to help scientists write expert-level empirical software.** Nature. 2026;654:909-916. doi:10.1038/s41586-026-10658-6.

Method used by VULCAN:

`problem -> generate candidate -> sandbox/objective evaluation -> score -> Flat-UCB/PUCT-style selection -> mutate -> repeat`

Reference implementation from Google Research:  
https://github.com/google-research/era

VULCAN independently implements the published search pattern; ERA source code is not vendored.

## 3. Objective verification principle

Generated software is not accepted because an LLM says it is correct. Candidate quality is evaluated by executable or deterministic checks. This follows the same broad principle used in software-agent benchmarks such as SWE-bench, where success is tied to repository tests rather than free-text judgement.  
https://github.com/SWE-bench/SWE-bench

MedAgentBench applies the same general idea to healthcare by testing agents in an executable FHIR environment.  
https://stanfordmlgroup.github.io/projects/medagentbench/

Implementation: `AcceptanceTestGenerator` + `ClinicGym` verifier.

## 4. Clinic ontology

VULCAN converts the flat environment inventory into a graph of clinic entities and relationships. The design is analogous to Palantir's ontology approach, which represents operational systems through object types, links, actions and shared properties.  
https://www.palantir.com/docs/foundry/ontologies/ontologies-overview

Implementation: `ClinicOntology` + `ClinicOntologyBuilder`.

## 5. Reusable trusted components

Successful application platforms reduce repeated engineering by composing reusable platform capabilities rather than recreating every function. ServiceNow explicitly supports reusable components and structured application phases from planning through testing, deployment and maintenance. Its Build Agent can generate applications from plain-language requirements.  
https://www.servicenow.com/docs/r/application-development/build-applications.html  
https://www.servicenow.com/docs/r/application-development/create-a-new-application-using-build-agent.html

Replit Agent is another useful software-on-demand analogy: a user describes an application and the agent builds and iterates on it in an integrated application environment.  
https://replit.com/products/agent

Implementation: `TrustedComponent` catalog + deterministic component selection.

## 6. Closed-loop simulation and rare failures

Waymo validates software through simulation, closed-course testing and staged real-world exposure, including rare or difficult scenarios. This supports VULCAN's principle that generated healthcare software should face simulated failures before any real clinical deployment.  
https://waymo.com/waymo-driver/  
https://waymo.com/blog/2026/02/the-waymo-world-model-a-new-frontier-for-autonomous-driving-simulation/

Implementation: `clinicgym/scenarios.json` with normal and fault scenarios.

## 7. Controlled deployment and rollback

Software generation is only one stage. VULCAN models promotion through `ClinicGym -> silent validation -> limited pilot`, with human approval, monitoring and rollback requirements. This mirrors mature enterprise software platforms where building, testing, deployment and maintenance are separate controlled phases.

Implementation: `DeploymentPlan`.

## 8. VULCAN hard rules

1. Missing required environment facts block generation.
2. Inferred or conflicting facts cannot satisfy required capabilities.
3. Required endpoints and integration capabilities must be explicitly collected.
4. SafetyGate is a hard constraint, not part of the optimization score.
5. Acceptance tests are defined before the candidate is accepted.
6. Generated code is evaluated objectively; unsafe candidates receive score zero.
7. ClinicGym precedes any real-world pilot.
8. Deployment requires monitoring and rollback capability.
9. Optimization may improve software quality but may never trade away safety or environment grounding.
