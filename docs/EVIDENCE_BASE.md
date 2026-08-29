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

For healthcare integrations, future evaluators should additionally verify resulting FHIR/DICOM state against sandbox systems rather than only inspect generated text.

## 4. VULCAN hard rules

1. Missing required environment facts block generation.
2. Inferred or conflicting facts cannot satisfy required capabilities.
3. Required endpoints and integration capabilities must be explicitly collected.
4. SafetyGate is a hard constraint, not part of the optimization score.
5. Generated code is evaluated objectively; unsafe candidates receive score zero.
6. Optimization may improve software quality but may never trade away safety or environment grounding.
