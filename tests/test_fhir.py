import httpx

from vulcan.core.compiler import IntentCompiler
from vulcan.interoperability.fhir import FHIRSandboxClient, build_rop_screening_bundle
from vulcan.models.spec import ROPCase


def _case() -> ROPCase:
    return ROPCase(
        patient_id="SYN-ROP-001",
        gestational_age_weeks=27.4,
        birth_weight_g=920,
        exam_postmenstrual_age_weeks=34.1,
        sex="female",
    )


def test_rop_bundle_contains_proposed_clinician_review_workflow():
    spec = IntentCompiler().compile(
        "Generate an ROP screening workflow with FHIR scheduling, DICOM images and clinician review."
    )
    bundle = build_rop_screening_bundle(spec, _case())
    resources = [entry["resource"] for entry in bundle["entry"]]
    by_type = {resource["resourceType"]: resource for resource in resources}

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "transaction"
    assert by_type["Appointment"]["status"] == "proposed"
    assert by_type["Task"]["status"] == "draft"
    assert by_type["Task"]["intent"] == "proposal"
    assert "Provenance" in by_type


def test_fhir_client_posts_transaction_bundle():
    spec = IntentCompiler().compile(
        "Generate an ROP screening workflow with FHIR scheduling and clinician review."
    )
    bundle = build_rop_screening_bundle(spec, _case())

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/fhir"
        return httpx.Response(
            200,
            json={
                "resourceType": "Bundle",
                "type": "transaction-response",
                "entry": [{"response": {"status": "201 Created"}}],
            },
        )

    client = FHIRSandboxClient(
        "http://testserver/fhir",
        transport=httpx.MockTransport(handler),
    )
    result = client.execute_transaction(bundle)

    assert result["status_code"] == 200
    assert result["resource_type"] == "Bundle"
    assert result["bundle_type"] == "transaction-response"
