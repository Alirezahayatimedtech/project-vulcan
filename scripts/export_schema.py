from __future__ import annotations

import json
from pathlib import Path

from vulcan.models.spec import SystemSpec


if __name__ == "__main__":
    destination = Path(__file__).resolve().parents[1] / "schemas" / "systemspec.schema.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(SystemSpec.model_json_schema(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(destination)
