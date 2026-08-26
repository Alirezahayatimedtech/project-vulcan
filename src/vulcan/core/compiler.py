from __future__ import annotations

import re

from vulcan.models.spec import (
    DataInput,
    Integration,
    RiskLevel,
    SystemSpec,
    WorkflowStep,
)


class IntentCompiler:
    """Deterministic prototype for need -> SystemSpec.

    This intentionally does not call an LLM. It proves the architecture while keeping
    behavior deterministic and testable. An LLM-backed compiler can later produce the
    same SystemSpec schema.
    """

    def compile(self, need: str) -> SystemSpec:
        text = need.lower()
        domain = self._infer_domain(text)
        risk = self._infer_risk(text)

        data_inputs: list[DataInput] = []
        integrations = [Integration(system="EHR", standard="FHIR", direction="read")]

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
            if term in text:
                data_inputs.append(DataInput(name=canonical, source="EHR", standard="FHIR"))

        if not data_inputs:
            data_inputs.append(DataInput(name="patient_record", source="EHR", standard="FHIR"))

        approval_requested = "approval" in text or risk in {
            RiskLevel.CLINICAL_DECISION_SUPPORT,
            RiskLevel.HIGH_RISK_AUTONOMOUS,
        }

        workflow_steps = [
            WorkflowStep(
                id="ingest",
                name="Ingest required data",
                actor="system",
                action="Retrieve the required structured and unstructured inputs.",
            ),
            WorkflowStep(
                id="evaluate",
                name="Evaluate patient state",
                actor="clinical-agent",
                action="Apply configured rules and models to generate a reviewable assessment.",
            ),
            WorkflowStep(
                id="review",
                name="Clinical review",
                actor="clinician",
                action="Review assessment, evidence and proposed next action.",
                requires_human_approval=approval_requested,
            ),
            WorkflowStep(
                id="record",
                name="Record outcome",
                actor="system",
                action="Persist approved result and audit metadata.",
                requires_human_approval=approval_requested,
            ),
        ]

        if any(term in text for term in ["follow-up", "follow up", "schedule"]):
            workflow_steps.append(
                WorkflowStep(
                    id="followup",
                    name="Coordinate follow-up",
                    actor="workflow-agent",
                    action="Prepare follow-up workflow after clinician approval.",
                    requires_human_approval=True,
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
            output_artifacts=["clinician_dashboard", "audit_log", "workflow_manifest"],
            human_approval_points=approval_points,
            risk_level=risk,
            audit_required=True,
            notes=[
                "Prototype specification generated deterministically.",
                "Clinical logic and model selection require domain-specific validation.",
            ],
        )

    @staticmethod
    def _infer_domain(text: str) -> str:
        if any(term in text for term in ["rop", "retina", "retinal", "ophthalm"]):
            return "ophthalmology"
        if any(term in text for term in ["cardiac", "cardiology", "heart"]):
            return "cardiology"
        if any(term in text for term in ["oncology", "cancer", "tumor"]):
            return "oncology"
        return "general"

    @staticmethod
    def _infer_risk(text: str) -> RiskLevel:
        high_risk = ["autonomous diagnosis", "autonomous treatment", "without approval", "emergency"]
        if any(term in text for term in high_risk):
            return RiskLevel.HIGH_RISK_AUTONOMOUS
        cds = ["diagnos", "treat", "risk", "recommend", "triage", "classif"]
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
