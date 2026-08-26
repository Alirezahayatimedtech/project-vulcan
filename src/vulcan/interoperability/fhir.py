from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import httpx

from vulcan.models.spec import ROPCase, SystemSpec

FHIR_JSON = "application/fhir+json"


def build_rop_screening_bundle(spec: SystemSpec, case: ROPCase) -> dict:
    """Build a FHIR R4 transaction bundle for a proposed ROP screening workflow.

    The bundle contains only research/sandbox artifacts. Appointment and Task are created
    in proposed/draft states and do not represent autonomous clinical orders.
    """
    run_id = uuid4().hex[:12]
    patient_ref = f"Patient/{case.patient_id}"
    appointment_id = f"rop-appt-{run_id}"
    task_id = f"rop-task-{run_id}"
    ga_id = f"ga-{run_id}"
    bw_id = f"bw-{run_id}"
    recorded = datetime.now(timezone.utc).isoformat()

    patient = {
        "resourceType": "Patient",
        "id": case.patient_id,
        "gender": case.sex,
        "identifier": [{"system": "urn:vulcan:synthetic-patient", "value": case.patient_id}],
    }
    ga = {
        "resourceType": "Observation",
        "id": ga_id,
        "status": "final",
        "code": {"text": "Gestational age at birth"},
        "subject": {"reference": patient_ref},
        "valueQuantity": {
            "value": case.gestational_age_weeks,
            "unit": "weeks",
            "system": "http://unitsofmeasure.org",
            "code": "wk",
        },
    }
    birth_weight = {
        "resourceType": "Observation",
        "id": bw_id,
        "status": "final",
        "code": {"text": "Birth weight"},
        "subject": {"reference": patient_ref},
        "valueQuantity": {
            "value": case.birth_weight_g,
            "unit": "g",
            "system": "http://unitsofmeasure.org",
            "code": "g",
        },
    }
    appointment = {
        "resourceType": "Appointment",
        "id": appointment_id,
        "status": "proposed",
        "description": "ROP screening appointment proposed by Project Vulcan research prototype",
        "serviceType": [{"text": "Retinopathy of prematurity screening"}],
        "participant": [
            {
                "actor": {"reference": patient_ref},
                "required": "required",
                "status": "needs-action",
            }
        ],
    }
    task = {
        "resourceType": "Task",
        "id": task_id,
        "status": "draft",
        "intent": "proposal",
        "code": {"text": "Clinician review of proposed ROP screening workflow"},
        "for": {"reference": patient_ref},
        "focus": {"reference": f"Appointment/{appointment_id}"},
        "note": [{"text": f"Generated from SystemSpec 0.2: {spec.name}"}],
    }
    provenance = {
        "resourceType": "Provenance",
        "id": f"prov-{run_id}",
        "recorded": recorded,
        "target": [
            {"reference": f"Appointment/{appointment_id}"},
            {"reference": f"Task/{task_id}"},
        ],
        "agent": [
            {
                "type": {"text": "software author"},
                "who": {"display": "Project Vulcan v0.2 research prototype"},
            }
        ],
    }

    resources = [patient, ga, birth_weight, appointment, task, provenance]
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": resource,
                "request": {
                    "method": "PUT",
                    "url": f"{resource['resourceType']}/{resource['id']}",
                },
            }
            for resource in resources
        ],
    }


class FHIRSandboxClient:
    """Minimal FHIR client intended for HAPI/SMART sandbox use only."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 20.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    def metadata(self) -> dict:
        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            response = client.get(
                f"{self.base_url}/metadata",
                headers={"Accept": FHIR_JSON},
            )
            response.raise_for_status()
            return response.json()

    def execute_transaction(self, bundle: dict) -> dict:
        if bundle.get("resourceType") != "Bundle" or bundle.get("type") != "transaction":
            raise ValueError("FHIR execution requires a transaction Bundle")
        with httpx.Client(timeout=self.timeout, transport=self.transport) as client:
            response = client.post(
                self.base_url,
                headers={"Content-Type": FHIR_JSON, "Accept": FHIR_JSON},
                json=bundle,
            )
            response.raise_for_status()
            payload = response.json()
            return {
                "status_code": response.status_code,
                "resource_type": payload.get("resourceType"),
                "bundle_type": payload.get("type"),
                "entry_count": len(payload.get("entry", [])),
                "response": payload,
            }
