from __future__ import annotations

from pydantic import BaseModel


class ClinicGymObservation(BaseModel):
    app_started: bool
    fhir_patient_retrieved: bool
    pacs_studies_retrieved: bool
    environment_contract_respected: bool
    unauthorized_write_detected: bool = False
    required_output_produced: bool


class ClinicGymVerifier:
    """Objective pass/fail contract for generated software in ClinicGym."""

    def verify(self, observation: ClinicGymObservation) -> dict:
        checks = {
            "app_started": observation.app_started,
            "fhir_patient_retrieved": observation.fhir_patient_retrieved,
            "pacs_studies_retrieved": observation.pacs_studies_retrieved,
            "environment_contract_respected": observation.environment_contract_respected,
            "no_unauthorized_write": not observation.unauthorized_write_detected,
            "required_output_produced": observation.required_output_produced,
        }
        passed = all(checks.values())
        score = sum(checks.values()) / len(checks)
        return {"passed": passed, "score": score, "checks": checks}
