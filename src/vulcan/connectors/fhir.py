from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FHIRConnector:
    """Interface placeholder for a FHIR server.

    Real deployments must implement authentication, scoped permissions, pagination,
    terminology validation, provenance and audit logging.
    """

    base_url: str

    def capability(self) -> dict:
        return {
            "standard": "FHIR",
            "base_url": self.base_url,
            "mode": "prototype",
            "writes_enabled": False,
        }
