from __future__ import annotations

import re

from vulcan.models.spec import (
    ClinicalActionType,
    DataInput,
    Integration,
    RiskLevel,
    SystemSpec,
    WorkflowStep,
)


class IntentCompiler:
    """Deterministic need -> SystemSpec compiler used as Vulcan's safe baseline.

    Model-backed planners may later emit the same schema, but execution still passes
    through independent deterministic validation and safety controls.
    """

    def compile(self, need: str) -> SystemSpec:
        text = need.lower()
        domain = self._infer_domain(text)
        risk = self._infer_risk(text)

        data_inputs: list[DataInput] = []
        integrations = [Integration(system="EHR", standard="FHIR R4", direction="read")]

        if self._is_rop(text):
            data_inputs.extend(
                [
                    DataInput(name="gestational_age", source="EHR", standard="FHIR R4"),
                    DataInput(name="birth_weight", source="EHR", standard="FHIR R4"),
                ]
            )

        if any(term in text for term in ["image", "retinal", "fundus", "oct", "dicom"]):
            data_inputs.append(
                DataInput(name="medical_imaging", source="imaging_system", standard="DICOM")
            )
            integrations.append(
                Integration(system="Imaging/PACS", standard="DICOM", direction="read")
            )

        for term, canonical in [
            ("gestational age", "gestational_age"),
            ("birth weight", "birth_weight"),
            ("previous visit", "prior_encounters"),
            ("lab", "laboratory_results"),
            ("medication", "medications"),
        ]:
            if term in text and canonical not in {item.name for item in data_inputs}:
                data_inputs.append(DataInput(name=canonical, source="EHR", standard="FHIR R4"))

        if not data_inputs:
            data_inputs.append(DataInput(name="patient_record", source="EHR", standard="FHIR R4"))

        schedule_requested = any(
            term in text for term in ["follow-up", "follow up", "schedule", "appointment"]
        )
        if schedule_requested:
            integrations.append(
                Integration(system="EHR Scheduling", standard="FHIR R4", direction="write")
            )

        approval_requested = (
            "approval" in text
            or "review" in text
            or risk in {RiskLevel.CLINICAL_DECISION_SUPPORT, RiskLevel.HIGH_RISK_AUTONOMOUS}
        )

        workflow_steps = [
            WorkflowStep(
                id="ingest",
                name="Ingest required data",
                actor="system",
                action="Retrieve the required structured and imaging inputs.",
                action_type=ClinicalActionType.RETRIEVE,
            ),
            WorkflowStep(
                id="evaluate",
                name="Evaluate patient state",
                actor="clinical-agent",
                action="Apply configured rules and models to generate a reviewable assessment.",
                action_type=ClinicalActionType.ASSESS,
            ),
            WorkflowStep(
                id="review",
                name="Clinical review",
                actor="clinician",
                action="Review assessment, evidence and proposed next action.",
                action_type=ClinicalActionType.INFORMATIONAL,
                requires_human_approval=approval_requested,
            ),
            WorkflowStep(
                id="record",
                name="Record approved outcome",
                actor="system",
                action="Persist only clinician-approved results and audit metadata.",
                action_type=ClinicalActionType.RECORD,
                requires_human_approval=approval_requested,
            ),
        ]

        if schedule_requested:
            workflow_steps.append(
                WorkflowStep(
                    id="followup",
                    name="Coordinate follow-up",
                    actor="workflow-agent",
                    action="Prepare an ROP follow-up appointment after clinician approval.",
                    action_type=ClinicalActionType.SCHEDULE,
                    requires_human_approval=True,
                )
            )

        if "discharge" in text:
            workflow_steps.append(
                WorkflowStep(
                    id="discharge",
                    name="Discharge action",
                    actor="clinical-agent",
                    action=need.strip(),
                    action_type=ClinicalActionType.DISCHARGE,
                    requires_human_approval="approval" in text,
                )
            )

        if any(term in text for term in ["oxygen", "fio2", "flow rate", "respiratory support"]):
            workflow_steps.append(
                WorkflowStep(
                    id="respiratory-change",
                    name="Respiratory support change",
                    actor="clinical-agent",
                    action=need.strip(),
                    action_type=ClinicalActionType.RESPIRATORY_SUPPORT_CHANGE,
                    requires_human_approval="approval" in text,
                )
            )

        name = self._make_name(domain, need)
        approval_points = [step.name for step in workflow_steps if step.requires_human_approval]

        return SystemSpec(
            name=name,
            objective=need.strip(),
            clinical_domain=domain,
            actors=["clinician", "patient", "clinical-agent", "workflow-agent"],
            data_inputs=data_inputs,
            integrations=integrations,
            workflow_steps=workflow_steps,
            output_artifacts=[
                "clinician_dashboard",
                "audit_log",
                "workflow_manifest",
                "fhir_bundle",
            ],
            human_approval_points=approval_points,
            risk_level=risk,
            audit_required=True,
            notes=[
                "Research prototype specification.",
                "Generated clinical actions remain subject to deterministic policy checks and human authority.",
            ],
        )

    @staticmethod
    def _is_rop(text: str) -> bool:
        return "rop" in text or "retinopathy of prematurity" in text

    @staticmethod
    def _infer_domain(text: str) -> str:
        if any(
            term in text
            for term in ["rop", "retinopathy of prematurity", "retina", "retinal", "ophthalm"]
        ):
            return "ophthalmology"
        if any(term in text for term in ["cardiac", "cardiology", "heart"]):
            return "cardiology"
        if any(term in text for term in ["oncology", "cancer", "tumor"]):
            return "oncology"
        return "general"

    @staticmethod
    def _infer_risk(text: str) -> RiskLevel:
        autonomous_markers = [
            "autonomous",
            "autonomously",
            "without approval",
            "no clinician",
            "without clinician",
        ]
        high_risk_actions = [
            "diagnos",
            "treat",
            "discharge",
            "oxygen",
            "fio2",
            "medication",
            "dose",
            "ventilat",
        ]
        if any(marker in text for marker in autonomous_markers) and any(
            re.search(action, text) for action in high_risk_actions
        ):
            return RiskLevel.HIGH_RISK_AUTONOMOUS
        cds = ["diagnos", "treat", "risk", "recommend", "triage", "classif", "screening"]
        if any(re.search(term, text) for term in cds):
            return RiskLevel.CLINICAL_DECISION_SUPPORT
        admin = ["schedule", "billing", "registry", "administrative"]
        if any(term in text for term in admin):
            return RiskLevel.ADMINISTRATIVE
        return RiskLevel.CLINICIAN_SUPPORT

    @staticmethod
    def _make_name(domain: str, need: str) -> str:
        short = " ".join(need.strip().split()[:6]).rstrip(".,")
        return f"VULCAN {domain.title()} System — {short}"
