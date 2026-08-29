from __future__ import annotations

from pydantic import BaseModel

# Design analogy: successful workflow/app platforms compose reusable trusted building blocks
# instead of regenerating every capability from scratch.
# ServiceNow application development: https://www.servicenow.com/docs/r/application-development/developing-applications.html
# Replit Agent product model: https://replit.com/products/agent


class TrustedComponent(BaseModel):
    id: str
    purpose: str
    required_facts: list[str]
    allowed_mode: str = "read_only"


COMPONENTS: dict[str, TrustedComponent] = {
    "fhir_patient_reader": TrustedComponent(
        id="fhir_patient_reader",
        purpose="Read patient demographics from a FHIR EHR.",
        required_facts=["ehr.fhir.supported", "ehr.fhir.base_url"],
    ),
    "dicom_study_retriever": TrustedComponent(
        id="dicom_study_retriever",
        purpose="Query and retrieve imaging studies from PACS.",
        required_facts=[
            "pacs.dicom.supported",
            "pacs.query_retrieve.supported",
            "pacs.dicom.host",
            "pacs.dicom.port",
            "pacs.dicom.ae_title",
        ],
    ),
    "audit_logger": TrustedComponent(
        id="audit_logger",
        purpose="Record application actions and provenance.",
        required_facts=[],
    ),
    "clinician_approval": TrustedComponent(
        id="clinician_approval",
        purpose="Require explicit human approval before clinical actions.",
        required_facts=[],
    ),
}


def select_components(need: str) -> list[TrustedComponent]:
    text = need.lower()
    selected = [COMPONENTS["audit_logger"]]
    if "ehr" in text or "fhir" in text or "patient" in text:
        selected.append(COMPONENTS["fhir_patient_reader"])
    if any(term in text for term in ["oct", "image", "fundus", "pacs", "dicom"]):
        selected.append(COMPONENTS["dicom_study_retriever"])
    if any(term in text for term in ["recommend", "risk", "diagnos", "triage", "treat"]):
        selected.append(COMPONENTS["clinician_approval"])
    return selected
