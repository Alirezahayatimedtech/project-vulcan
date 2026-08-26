from pathlib import Path

from vulcan.evals.golden import run_golden


def test_golden_rop_suite_passes():
    path = Path(__file__).resolve().parents[1] / "evals" / "golden_rop.json"
    report = run_golden(path)

    assert report["passed"] == report["total"]
    assert report["pass_rate"] == 1.0
