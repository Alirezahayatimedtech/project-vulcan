from __future__ import annotations

from vulcan.models.spec import RiskLevel, SafetyFinding, SystemSpec


class SafetyGate:
    """Prototype static safety analysis for generated healthcare systems."""

    def evaluate(self, spec: SystemSpec) -> tuple[list[SafetyFinding], bool]:
        findings: list[SafetyFinding] = []

        if not spec.audit_required:
            findings.append(
                SafetyFinding(
                    severity="block",
                    code="AUDIT_REQUIRED",
                    message="Healthcare workflows must retain an audit trail.",
                )
            )

        if spec.risk_level == RiskLevel.HIGH_RISK_AUTONOMOUS:
            findings.append(
                SafetyFinding(
                    severity="block",
                    code="AUTONOMY_BLOCKED",
                    message="High-risk autonomous clinical actions are blocked in the prototype.",
                )
            )

        if spec.risk_level == RiskLevel.CLINICAL_DECISION_SUPPORT and not spec.human_approval_points:
            findings.append(
                SafetyFinding(
                    severity="block",
                    code="HUMAN_REVIEW_MISSING",
                    message="Clinical decision support requires a defined human approval point.",
                )
            )

        write_integrations = [i for i in spec.integrations if i.direction in {"write", "read_write"}]
        if write_integrations:
            findings.append(
                SafetyFinding(
                    severity="warning",
                    code="WRITE_INTEGRATION",
                    message="Write access requires explicit permission, sandbox testing and audit controls.",
                )
            )

        if not findings:
            findings.append(
                SafetyFinding(
                    severity="info",
                    code="STATIC_CHECKS_PASSED",
                    message="Prototype static checks passed; simulation and expert review are still required.",
                )
            )

        deployable = not any(f.severity == "block" for f in findings)
        return findings, deployable
