from vulcan.core.compiler import IntentCompiler
from vulcan.safety.gate import SafetyGate


def test_v02_smoke():
    spec = IntentCompiler().compile(
        "Generate an ROP screening workflow with FHIR scheduling, DICOM routing, and clinician review."
    )
    findings, deployable = SafetyGate().evaluate(spec)
    assert deployable is True
    assert any(integration.standard == "DICOM" for integration in spec.integrations)
    assert not any(finding.severity == "block" for finding in findings)
