from vulcan.evolution.engine import VulcanEvolutionEngine
from vulcan.evolution.models import EvolutionRequest
from vulcan.models.environment import EnvironmentFact, EnvironmentSpec, EvidenceStatus


def environment() -> EnvironmentSpec:
    facts = [
        EnvironmentFact(key="ehr.present", value=True, status=EvidenceStatus.DECLARED),
        EnvironmentFact(key="ehr.fhir.supported", value=True, status=EvidenceStatus.VERIFIED),
        EnvironmentFact(
            key="ehr.fhir.capability_statement",
            value="captured",
            status=EvidenceStatus.DISCOVERED,
        ),
        EnvironmentFact(
            key="ehr.fhir.base_url",
            value="https://ehr.test/fhir",
            status=EvidenceStatus.VERIFIED,
        ),
        EnvironmentFact(key="pacs.present", value=True, status=EvidenceStatus.DECLARED),
        EnvironmentFact(
            key="network.integration_available",
            value=True,
            status=EvidenceStatus.VERIFIED,
        ),
        EnvironmentFact(key="pacs.dicom.supported", value=True, status=EvidenceStatus.VERIFIED),
        EnvironmentFact(
            key="pacs.query_retrieve.supported",
            value=True,
            status=EvidenceStatus.VERIFIED,
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


def test_evolution_improves_candidate_and_uses_grounded_integrations():
    result = VulcanEvolutionEngine().evolve(
        EvolutionRequest(
            need="Build a read-only ophthalmology app for EHR data and OCT images from PACS.",
            environment=environment(),
            iterations=8,
        )
    )

    assert result.environment_ready is True
    assert result.best_candidate is not None
    assert result.best_candidate.hard_gate_passed is True
    assert result.best_candidate.score > result.search_trace[0].score
    assert "app/integrations/fhir.py" in result.best_candidate.files
    assert "app/integrations/dicom.py" in result.best_candidate.files
    assert "tests/test_contract.py" in result.best_candidate.files


def test_evolution_blocks_when_required_fact_is_unknown():
    clinic = environment()
    for fact in clinic.facts:
        if fact.key == "pacs.dicom.host":
            fact.status = EvidenceStatus.UNKNOWN
            fact.value = None

    result = VulcanEvolutionEngine().evolve(
        EvolutionRequest(
            need="Build a read-only OCT viewer connected to PACS.",
            environment=clinic,
            iterations=4,
        )
    )

    assert result.environment_ready is False
    assert result.best_candidate is None
    assert "pacs.dicom.host" in result.readiness.missing_facts
