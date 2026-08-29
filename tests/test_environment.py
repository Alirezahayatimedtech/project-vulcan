from vulcan.environment.gate import EnvironmentGate
from vulcan.models.environment import EnvironmentFact, EnvironmentSpec, EvidenceStatus


def test_missing_environment_facts_block_generation():
    environment = EnvironmentSpec(
        clinic_name="Example Eye Clinic",
        facts=[
            EnvironmentFact(
                key="ehr.present",
                value=True,
                status=EvidenceStatus.DECLARED,
                source_type="clinic_interview",
            )
        ],
    )

    readiness = EnvironmentGate().evaluate(
        "Build software that reads OCT images from PACS using DICOM.",
        environment,
    )

    assert readiness.ready is False
    assert "ehr.fhir.supported" in readiness.missing_facts
    assert "pacs.dicom.host" in readiness.missing_facts


def verified_eye_clinic() -> EnvironmentSpec:
    facts = [
        EnvironmentFact(key="ehr.present", value=True, status=EvidenceStatus.DECLARED),
        EnvironmentFact(
            key="ehr.fhir.supported",
            value=True,
            status=EvidenceStatus.VERIFIED,
            source_type="fhir_metadata_probe",
        ),
        EnvironmentFact(
            key="ehr.fhir.capability_statement",
            value="captured",
            status=EvidenceStatus.DISCOVERED,
            source_type="fhir_capability_statement",
        ),
        EnvironmentFact(
            key="ehr.fhir.base_url",
            value="https://ehr.test/fhir",
            status=EvidenceStatus.VERIFIED,
            source_type="fhir_metadata_probe",
        ),
        EnvironmentFact(key="pacs.present", value=True, status=EvidenceStatus.DECLARED),
        EnvironmentFact(
            key="network.integration_available",
            value=True,
            status=EvidenceStatus.VERIFIED,
        ),
        EnvironmentFact(
            key="pacs.dicom.supported",
            value=True,
            status=EvidenceStatus.VERIFIED,
            source_type="dicom_conformance_statement",
        ),
        EnvironmentFact(
            key="pacs.query_retrieve.supported",
            value=True,
            status=EvidenceStatus.VERIFIED,
            source_type="dicom_conformance_statement",
        ),
        EnvironmentFact(
            key="pacs.dicom.host",
            value="pacs.internal",
            status=EvidenceStatus.VERIFIED,
        ),
        EnvironmentFact(key="pacs.dicom.port", value=104, status=EvidenceStatus.VERIFIED),
        EnvironmentFact(
            key="pacs.dicom.ae_title",
            value="EYE_PACS",
            status=EvidenceStatus.VERIFIED,
        ),
    ]
    return EnvironmentSpec(clinic_name="Example Eye Clinic", facts=facts)


def test_verified_environment_can_pass_readiness_gate():
    readiness = EnvironmentGate().evaluate(
        "Build software that reads OCT images from PACS using DICOM.",
        verified_eye_clinic(),
    )

    assert readiness.ready is True
    assert readiness.missing_facts == []
    assert readiness.unusable_facts == []


def test_inferred_fact_is_not_usable_for_generation():
    environment = verified_eye_clinic()
    for fact in environment.facts:
        if fact.key == "network.integration_available":
            fact.status = EvidenceStatus.INFERRED

    readiness = EnvironmentGate().evaluate("Build a clinic dashboard.", environment)

    assert readiness.ready is False
    assert "network.integration_available" in readiness.unusable_facts


def test_known_but_unsupported_capability_is_blocked():
    environment = verified_eye_clinic()
    for fact in environment.facts:
        if fact.key == "ehr.fhir.supported":
            fact.value = False

    readiness = EnvironmentGate().evaluate("Build a clinic dashboard.", environment)

    assert readiness.ready is False
    assert "ehr.fhir.supported" in readiness.unusable_facts
