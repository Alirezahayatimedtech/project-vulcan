from __future__ import annotations

from vulcan.models.environment import (
    EnvironmentReadiness,
    EnvironmentSpec,
    EvidenceStatus,
)

TRUSTED_STATUSES = {
    EvidenceStatus.VERIFIED,
    EvidenceStatus.DISCOVERED,
    EvidenceStatus.DECLARED,
}


class EnvironmentGate:
    """Fail closed when required clinic facts are missing or inferred."""

    BASE_REQUIRED = [
        "ehr.present",
        "pacs.present",
        "network.integration_available",
    ]

    def required_facts(self, need: str) -> list[str]:
        text = need.lower()
        required = list(self.BASE_REQUIRED)

        if "fhir" in text or "ehr" in text:
            required.extend(
                [
                    "ehr.fhir.supported",
                    "ehr.fhir.capability_statement",
                ]
            )

        if any(term in text for term in ["image", "oct", "fundus", "pacs", "dicom"]):
            required.extend(
                [
                    "pacs.dicom.supported",
                    "pacs.query_retrieve.supported",
                ]
            )

        return list(dict.fromkeys(required))

    def evaluate(self, need: str, environment: EnvironmentSpec) -> EnvironmentReadiness:
        facts = environment.fact_map()
        required = self.required_facts(need)
        missing: list[str] = []
        unusable: list[str] = []

        for key in required:
            fact = facts.get(key)
            if fact is None or fact.status == EvidenceStatus.UNKNOWN or fact.value is None:
                missing.append(key)
                continue
            if fact.status not in TRUSTED_STATUSES:
                unusable.append(key)

        return EnvironmentReadiness(
            ready=not missing and not unusable,
            required_facts=required,
            missing_facts=missing,
            unusable_facts=unusable,
        )
