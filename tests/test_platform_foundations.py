from vulcan.acceptance import AcceptanceTestGenerator
from vulcan.components import select_components
from vulcan.deployment import default_deployment_plan
from vulcan.models.environment import EnvironmentFact, EnvironmentSpec, EvidenceStatus
from vulcan.ontology import ClinicOntologyBuilder


def test_clinic_ontology_is_built_from_collected_facts():
    environment = EnvironmentSpec(
        clinic_name="Synthetic Eye Clinic",
        facts=[
            EnvironmentFact(
                key="ehr.present",
                value=True,
                status=EvidenceStatus.VERIFIED,
                source="clinic_inventory",
            )
        ],
    )
    ontology = ClinicOntologyBuilder().build(environment)

    assert any(entity.id == "clinic" for entity in ontology.entities)
    assert any(entity.id == "ehr" for entity in ontology.entities)
    assert any(entity.id == "fact:ehr.present" for entity in ontology.entities)
    assert any(relation.source == "ehr" and relation.relation == "has_fact" for relation in ontology.relations)


def test_need_selects_trusted_blocks_and_acceptance_contract():
    need = "Build an app that reads patient EHR data and previous OCT images from PACS."
    components = select_components(need)
    acceptance = AcceptanceTestGenerator().generate(need)

    component_ids = {component.id for component in components}
    test_ids = {test.id for test in acceptance.tests}

    assert "fhir_patient_reader" in component_ids
    assert "dicom_study_retriever" in component_ids
    assert "AT-FHIR-001" in test_ids
    assert "AT-DICOM-001" in test_ids


def test_deployment_requires_clinicgym_before_pilot():
    plan = default_deployment_plan()
    assert plan.stages[0].name == "clinicgym"
    assert plan.stages[-1].name == "limited_pilot"
    assert plan.rollback_required is True
