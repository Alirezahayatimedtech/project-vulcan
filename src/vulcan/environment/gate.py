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
    """Fail closed when required clinic facts are missing, inferred, or unavailable."""

    BASE_REQUIRED = [
        "ehr.present",
        "ehr.fhir.supported",
        "ehr.fhir.capability_statement",
        "ehr.fhir.base_url",
        "pacs.present",
        "network.integration_available",
    ]

    def required_facts(self, need: str) -> list[str]:
        text = need.lower()
        required = list(self.BASE_REQUIRED)

        if any(term in text for term in ["image", "oct", "fundus", "pacs", "dicom"]):
            required.extend(
                [
                    "pacs.dicom.supported",
                    "pacs.query_retrieve.supported",
                    "pacs.dicom.host",
                    "pacs.dicom.port",
                    "pacs.dicom.ae_title",
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
            if fact.status not in TRUSTED_STATUSES or fact.value in (False, "", [], {}):
                unusable.append(key)

        return EnvironmentReadiness(
            ready=not missing and not unusable,
            required_facts=required,
            missing_facts=missing,
            unusable_facts=unusable,
        )
