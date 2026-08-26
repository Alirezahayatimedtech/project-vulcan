from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DICOMConnector:
    endpoint: str

    def capability(self) -> dict:
        return {
            "standard": "DICOM",
            "endpoint": self.endpoint,
            "mode": "prototype",
            "writes_enabled": False,
        }
