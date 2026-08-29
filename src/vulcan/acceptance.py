from __future__ import annotations

from pydantic import BaseModel, Field

# Principle: define verifiable success before/alongside code generation.
# SWE-bench: repository tasks are judged by executable tests.
# https://github.com/SWE-bench/SWE-bench
# MedAgentBench: healthcare-agent tasks are evaluated in an executable FHIR environment.
# https://stanfordmlgroup.github.io/projects/medagentbench/


class AcceptanceTest(BaseModel):
    id: str
    requirement: str
    verifier: str
    hard_gate: bool = True


class AcceptancePlan(BaseModel):
    tests: list[AcceptanceTest] = Field(default_factory=list)


class AcceptanceTestGenerator:
    def generate(self, need: str) -> AcceptancePlan:
        text = need.lower()
        tests = [
            AcceptanceTest(
                id="AT-001",
                requirement="Application starts successfully.",
                verifier="health_endpoint_returns_200",
            ),
            AcceptanceTest(
                id="AT-002",
                requirement="Application uses only collected EnvironmentSpec capabilities.",
                verifier="no_undeclared_endpoints_or_capabilities",
            ),
            AcceptanceTest(
                id="AT-003",
                requirement="No unauthorized clinical or infrastructure write occurs.",
                verifier="no_unauthorized_write",
            ),
        ]
        if "ehr" in text or "fhir" in text or "patient" in text:
            tests.append(
                AcceptanceTest(
                    id="AT-FHIR-001",
                    requirement="Correct patient data can be retrieved from the configured FHIR server.",
                    verifier="fhir_patient_roundtrip",
                )
            )
        if any(term in text for term in ["oct", "image", "fundus", "pacs", "dicom"]):
            tests.append(
                AcceptanceTest(
                    id="AT-DICOM-001",
                    requirement="Required imaging studies can be queried and retrieved from PACS.",
                    verifier="pacs_query_retrieve_roundtrip",
                )
            )
        if any(term in text for term in ["recommend", "risk", "diagnos", "triage", "treat"]):
            tests.append(
                AcceptanceTest(
                    id="AT-SAFE-001",
                    requirement="Clinical output requires the configured human approval point.",
                    verifier="human_approval_required",
                )
            )
        return AcceptancePlan(tests=tests)
