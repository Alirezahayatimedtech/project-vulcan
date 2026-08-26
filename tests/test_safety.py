from vulcan.core.compiler import IntentCompiler
from vulcan.safety.gate import SafetyGate


def test_high_risk_autonomy_is_blocked():
    spec = IntentCompiler().compile(
        "Build a system for autonomous diagnosis and treatment of emergency patients without approval."
    )
    findings, deployable = SafetyGate().evaluate(spec)

    assert deployable is False
    assert any(f.code == "AUTONOMY_BLOCKED" for f in findings)


def test_supervised_rop_workflow_passes_static_gate():
    spec = IntentCompiler().compile(
        "Build an ROP risk screening system that recommends follow-up and requires clinician approval."
    )
    findings, deployable = SafetyGate().evaluate(spec)

    assert deployable is True
    assert not any(f.severity == "block" for f in findings)
