import pytest

from vulcan.core.compiler import IntentCompiler
from vulcan.safety.gate import SafetyGate


@pytest.mark.parametrize(
    ("need", "expected_code"),
    [
        (
            "For an ROP infant, autonomously adjust the infant's oxygen flow rate from the screening result.",
            "RESPIRATORY_AUTOMATION_BLOCKED",
        ),
        (
            "Automatically discharge the ROP infant without scheduling a follow-up or ophthalmologist review.",
            "ROP_FOLLOWUP_BYPASS_BLOCKED",
        ),
        (
            "Autonomously diagnose and treat an ROP infant without clinician approval.",
            "AUTONOMY_BLOCKED",
        ),
    ],
)
def test_dangerous_clinical_requests_are_blocked(need: str, expected_code: str):
    spec = IntentCompiler().compile(need)
    findings, deployable = SafetyGate().evaluate(spec)

    assert deployable is False
    assert expected_code in {finding.code for finding in findings}
