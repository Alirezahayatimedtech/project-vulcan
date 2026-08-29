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
    assert "pacs.present" in readiness.missing_facts
    assert "pacs.dicom.supported" in readiness.missing_facts


def test_verified_environment_can_pass_readiness_gate():
    facts = [
        EnvironmentFact(key="ehr.present", value=True, status=EvidenceStatus.DECLARED),
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
    ]
    environment = EnvironmentSpec(clinic_name="Example Eye Clinic", facts=facts)

    readiness = EnvironmentGate().evaluate(
        "Build software that reads OCT images from PACS using DICOM.",
        environment,
    )

    assert readiness.ready is True
    assert readiness.missing_facts == []
    assert readiness.unusable_facts == []


def test_inferred_fact_is_not_usable_for_generation():
    facts = [
        EnvironmentFact(key="ehr.present", value=True, status=EvidenceStatus.DECLARED),
        EnvironmentFact(key="pacs.present", value=True, status=EvidenceStatus.DECLARED),
        EnvironmentFact(
            key="network.integration_available",
            value=True,
            status=EvidenceStatus.INFERRED,
        ),
    ]
    environment = EnvironmentSpec(clinic_name="Example Eye Clinic", facts=facts)

    readiness = EnvironmentGate().evaluate("Build a clinic dashboard.", environment)

    assert readiness.ready is False
    assert "network.integration_available" in readiness.unusable_facts
