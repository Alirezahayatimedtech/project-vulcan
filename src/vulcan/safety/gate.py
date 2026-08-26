from __future__ import annotations

import re

from vulcan.models.spec import ClinicalActionType, RiskLevel, SafetyFinding, SystemSpec


DANGEROUS_ACTIONS = {
    ClinicalActionType.CLINICAL_ORDER,
    ClinicalActionType.MEDICATION_CHANGE,
    ClinicalActionType.RESPIRATORY_SUPPORT_CHANGE,
    ClinicalActionType.DISCHARGE,
}


class SafetyGate:
    """Deterministic policy enforcement for generated healthcare systems.

    This gate is intentionally independent of the model/planner. A critic model may add
    observations, but it cannot waive these rules.
    """

    def evaluate(self, spec: SystemSpec) -> tuple[list[SafetyFinding], bool]:
        findings: list[SafetyFinding] = []
        objective = spec.objective.lower()

        if not spec.audit_required:
            findings.append(
                self._block(
                    "AUDIT_REQUIRED",
                    "Healthcare workflows must retain an audit trail.",
                )
            )

        if spec.risk_level == RiskLevel.HIGH_RISK_AUTONOMOUS:
            findings.append(
                self._block(
                    "AUTONOMY_BLOCKED",
                    "High-risk autonomous clinical actions are blocked in the research prototype.",
                )
            )

        if (
            spec.risk_level == RiskLevel.CLINICAL_DECISION_SUPPORT
            and not spec.human_approval_points
        ):
            findings.append(
                self._block(
                    "HUMAN_REVIEW_MISSING",
                    "Clinical decision support requires a defined clinician approval point.",
                )
            )

        self._check_dangerous_workflow_actions(spec, findings)
        self._check_rop_guardrails(spec, objective, findings)

        write_integrations = [
            integration
            for integration in spec.integrations
            if integration.direction in {"write", "read_write"}
        ]
        if write_integrations:
            findings.append(
                SafetyFinding(
                    severity="warning",
                    code="WRITE_INTEGRATION",
                    message=(
                        "Write access is sandbox-only until authorization, audit and human "
                        "approval are verified."
                    ),
                )
            )

        if not findings:
            findings.append(
                SafetyFinding(
                    severity="info",
                    code="STATIC_CHECKS_PASSED",
                    message=(
                        "Deterministic checks passed; this is not clinical validation or "
                        "regulatory clearance."
                    ),
                )
            )

        deployable = not any(finding.severity == "block" for finding in findings)
        return self._dedupe(findings), deployable

    def _check_dangerous_workflow_actions(
        self,
        spec: SystemSpec,
        findings: list[SafetyFinding],
    ) -> None:
        for step in spec.workflow_steps:
            if step.action_type in DANGEROUS_ACTIONS and not step.requires_human_approval:
                findings.append(
                    self._block(
                        "CLINICAL_ACTION_REQUIRES_HUMAN",
                        (
                            f"'{step.name}' is a high-impact clinical action and requires "
                            "explicit human approval."
                        ),
                    )
                )

    def _check_rop_guardrails(
        self,
        spec: SystemSpec,
        objective: str,
        findings: list[SafetyFinding],
    ) -> None:
        is_rop = "rop" in objective or "retinopathy of prematurity" in objective
        if not is_rop:
            return

        if re.search(r"\b(discharge|send home)\b", objective) and re.search(
            r"without.*follow|no.*follow",
            objective,
        ):
            findings.append(
                self._block(
                    "ROP_FOLLOWUP_BYPASS_BLOCKED",
                    "ROP workflow cannot bypass required follow-up or ophthalmology review.",
                )
            )

        respiratory_terms = ["oxygen", "fio2", "flow rate", "respiratory support"]
        action_terms = ["adjust", "increase", "decrease", "set", "autonomous"]
        if any(term in objective for term in respiratory_terms) and any(
            term in objective for term in action_terms
        ):
            findings.append(
                self._block(
                    "RESPIRATORY_AUTOMATION_BLOCKED",
                    (
                        "Vulcan may not autonomously change oxygen or respiratory support "
                        "in this prototype."
                    ),
                )
            )

    @staticmethod
    def _block(code: str, message: str) -> SafetyFinding:
        return SafetyFinding(severity="block", code=code, message=message)

    @staticmethod
    def _dedupe(findings: list[SafetyFinding]) -> list[SafetyFinding]:
        unique: list[SafetyFinding] = []
        seen: set[str] = set()
        for finding in findings:
            if finding.code not in seen:
                seen.add(finding.code)
                unique.append(finding)
        return unique
