from __future__ import annotations

import json
from pathlib import Path

from vulcan.core.compiler import IntentCompiler
from vulcan.safety.gate import SafetyGate


def evaluate_case(case: dict) -> dict:
    spec = IntentCompiler().compile(case["need"])
    findings, deployable = SafetyGate().evaluate(spec)
    codes = {finding.code for finding in findings}
    standards = {integration.standard for integration in spec.integrations}
    step_ids = {step.id for step in spec.workflow_steps}

    checks = {
        "deployable": deployable == case["expected_deployable"],
        "domain": spec.clinical_domain == case.get("expected_domain", spec.clinical_domain),
        "standards": set(case.get("required_standards", [])).issubset(standards),
        "steps": set(case.get("required_steps", [])).issubset(step_ids),
        "safety_codes": set(case.get("required_safety_codes", [])).issubset(codes),
    }
    return {
        "id": case["id"],
        "passed": all(checks.values()),
        "checks": checks,
        "deployable": deployable,
        "safety_codes": sorted(codes),
    }


def run_golden(path: str | Path) -> dict:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    results = [evaluate_case(case) for case in cases]
    passed = sum(result["passed"] for result in results)
    return {
        "total": len(results),
        "passed": passed,
        "pass_rate": passed / len(results) if results else 0.0,
        "results": results,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    report = run_golden(root / "evals" / "golden_rop.json")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
