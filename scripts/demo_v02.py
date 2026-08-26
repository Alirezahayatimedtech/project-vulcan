from __future__ import annotations

import json
import os
import time

import httpx

API = os.getenv("VULCAN_URL", "http://localhost:8000").rstrip("/")
FHIR = os.getenv("FHIR_PUBLIC_URL", "http://localhost:8080/fhir").rstrip("/")

payload = {
    "need": (
        "Generate a screening workflow for Retinopathy of Prematurity for infants born at "
        "<30 weeks gestation, including FHIR scheduling and DICOM image routing, with clinician review."
    ),
    "case": {
        "patient_id": "SYN-ROP-001",
        "gestational_age_weeks": 27.4,
        "birth_weight_g": 920,
        "exam_postmenstrual_age_weeks": 34.1,
        "sex": "female",
    },
    "execute_fhir": True,
}

for _ in range(30):
    try:
        if httpx.get(f"{FHIR}/metadata", timeout=3).is_success:
            break
    except httpx.HTTPError:
        pass
    time.sleep(2)
else:
    raise SystemExit("HAPI FHIR did not become ready")

response = httpx.post(f"{API}/v1/forge/rop", json=payload, timeout=30)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
