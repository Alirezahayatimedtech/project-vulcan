# Safety and Regulation

Vulcan is research-only.

It is not a medical device, not validated for clinical use, and must not be used for diagnosis, treatment, triage or autonomous patient management.

## Current safety rules

- No real patient data in the repository.
- No autonomous diagnosis.
- No autonomous treatment.
- No EHR writes.
- No ordering, referral or patient-contact action.
- Human approval is required for clinical-decision-support workflows.
- Static safety checks must pass before any manifest is considered deployable in a sandbox.

## Prototype gate

The current `SafetyGate` blocks high-risk autonomous requests and requires human review for clinical decision support.

## Future safety requirements

- FHIR profile validation.
- DICOM de-identification checks.
- Provenance logging.
- Model versioning.
- Calibration and subgroup evaluation.
- Simulation before deployment.
- Prospective silent validation before clinical influence.
