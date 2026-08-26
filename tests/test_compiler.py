from vulcan.core.compiler import IntentCompiler
from vulcan.models.spec import RiskLevel


def test_rop_need_compiles_to_ophthalmology_cds():
    need = (
        "Build an ROP screening workflow using gestational age, birth weight, retinal images "
        "and previous visits. Flag high-risk infants, recommend follow-up, and require clinician approval."
    )
    spec = IntentCompiler().compile(need)

    assert spec.clinical_domain == "ophthalmology"
    assert spec.risk_level == RiskLevel.CLINICAL_DECISION_SUPPORT
    assert "Clinical review" in spec.human_approval_points
    assert any(i.standard == "DICOM" for i in spec.integrations)
    assert any(d.name == "gestational_age" for d in spec.data_inputs)
