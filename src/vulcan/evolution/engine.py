from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from vulcan.core.compiler import IntentCompiler
from vulcan.environment.gate import EnvironmentGate
from vulcan.evolution.models import CodingCandidate, EvolutionRequest, EvolutionResult
from vulcan.models.environment import EnvironmentSpec
from vulcan.models.spec import SystemSpec
from vulcan.safety.gate import SafetyGate

# Methodological basis:
# Aygun et al. Nature 2026, doi:10.1038/s41586-026-10658-6
# Reference implementation: https://github.com/google-research/era
# VULCAN implements the published generate -> execute/score -> Flat-UCB search pattern
# independently; ERA source code is not vendored here.


@dataclass(frozen=True)
class EvolutionTask:
    need: str
    environment: EnvironmentSpec
    specification: SystemSpec


class Generate(Protocol):
    def __call__(self, task: EvolutionTask, parent: CodingCandidate) -> CodingCandidate:
        ...


class Evaluate(Protocol):
    def __call__(self, task: EvolutionTask, candidate: CodingCandidate) -> CodingCandidate:
        ...


@dataclass
class SearchNode:
    candidate: CodingCandidate
    parent_index: int | None
    visits: int = 1
    rank_score: float = 0.5
    acquisition: float = 0.5


class FlatUCBSearch:
    """ERA-inspired global candidate search with rank-based PUCT exploration."""

    def __init__(self, c_puct: float = 1.0):
        self.c_puct = c_puct

    @staticmethod
    def _rank(nodes: list[SearchNode]) -> None:
        if len(nodes) == 1:
            nodes[0].rank_score = 1.0
            return
        ordered = sorted(nodes, key=lambda node: node.candidate.score)
        denominator = len(nodes) - 1
        for rank, node in enumerate(ordered):
            node.rank_score = rank / denominator

    def _acquire(self, nodes: list[SearchNode]) -> SearchNode:
        self._rank(nodes)
        prior = 1 / len(nodes)
        total_visits = sum(node.visits for node in nodes)
        for node in nodes:
            exploration = prior * math.sqrt(total_visits) / (1 + node.visits)
            node.acquisition = node.rank_score + self.c_puct * exploration
        return max(nodes, key=lambda node: node.acquisition)

    @staticmethod
    def _backpropagate(nodes: list[SearchNode], index: int) -> None:
        current: int | None = index
        while current is not None:
            nodes[current].visits += 1
            current = nodes[current].parent_index

    def run(
        self,
        task: EvolutionTask,
        seed: CodingCandidate,
        generate: Generate,
        evaluate: Evaluate,
        iterations: int,
    ) -> list[CodingCandidate]:
        seed = evaluate(task, seed)
        nodes = [SearchNode(candidate=seed, parent_index=None)]
        for _ in range(iterations):
            parent = self._acquire(nodes)
            parent_index = nodes.index(parent)
            child = evaluate(task, generate(task, parent.candidate))
            nodes.append(SearchNode(candidate=child, parent_index=parent_index))
            self._backpropagate(nodes, len(nodes) - 1)
        return [node.candidate for node in nodes]


class EvidenceGroundedCoder:
    """Draft coding roles that only use facts supplied in EnvironmentSpec."""

    @staticmethod
    def seed(task: EvolutionTask) -> CodingCandidate:
        environment = task.environment.model_dump_json(indent=2)
        return CodingCandidate(
            id="candidate-0",
            files={"environment.json": environment},
            logs=["Seeded only from collected EnvironmentSpec facts."],
        )

    @staticmethod
    def _needs_fhir(need: str) -> bool:
        text = need.lower()
        return "fhir" in text or "ehr" in text

    @staticmethod
    def _needs_dicom(need: str) -> bool:
        text = need.lower()
        return any(term in text for term in ["image", "oct", "fundus", "pacs", "dicom"])

    def __call__(self, task: EvolutionTask, parent: CodingCandidate) -> CodingCandidate:
        child = parent.model_copy(deep=True)
        child.parent_id = parent.id
        child.generation = parent.generation + 1
        child.id = f"{parent.id}.{child.generation}"

        if "APP_SPEC.md" not in child.files:
            child.role = "architect"
            child.files["APP_SPEC.md"] = self._architecture(task)
        elif "app/main.py" not in child.files:
            child.role = "backend-engineer"
            child.files["app/main.py"] = self._backend()
        elif self._needs_fhir(task.need) and "app/integrations/fhir.py" not in child.files:
            child.role = "integration-engineer"
            child.files["app/integrations/fhir.py"] = self._fhir()
        elif self._needs_dicom(task.need) and "app/integrations/dicom.py" not in child.files:
            child.role = "integration-engineer"
            child.files["app/integrations/dicom.py"] = self._dicom()
        elif "tests/test_contract.py" not in child.files:
            child.role = "test-engineer"
            child.files["tests/test_contract.py"] = self._tests()
        else:
            child.role = "evidence-reviewer"
            child.files["EVIDENCE.md"] = self._evidence()

        child.logs.append(f"Mutation produced by role: {child.role}")
        return child

    @staticmethod
    def _architecture(task: EvolutionTask) -> str:
        return (
            "# Generated application specification\n\n"
            f"Need: {task.need}\n\n"
            "Source of truth: environment.json. Unsupported or unknown capabilities must not "
            "be invented.\n\n"
            f"Clinical domain: {task.specification.clinical_domain}\n"
        )

    @staticmethod
    def _backend() -> str:
        return '''import json\nfrom pathlib import Path\n\nfrom fastapi import FastAPI\n\napp = FastAPI(title="VULCAN generated application")\nROOT = Path(__file__).resolve().parents[1]\n\n\n@app.get("/health")\ndef health() -> dict:\n    return {"status": "ok"}\n\n\n@app.get("/environment")\ndef environment() -> dict:\n    return json.loads((ROOT / "environment.json").read_text())\n'''

    @staticmethod
    def _fhir() -> str:
        return '''def get_fhir_config(environment: dict) -> dict:\n    facts = {item["key"]: item for item in environment["facts"]}\n    return {\n        "base_url": facts["ehr.fhir.base_url"]["value"],\n        "capability_statement": facts["ehr.fhir.capability_statement"]["value"],\n        "mode": "read-only",\n    }\n'''

    @staticmethod
    def _dicom() -> str:
        return '''def get_dicom_config(environment: dict) -> dict:\n    facts = {item["key"]: item for item in environment["facts"]}\n    return {\n        "host": facts["pacs.dicom.host"]["value"],\n        "port": facts["pacs.dicom.port"]["value"],\n        "ae_title": facts["pacs.dicom.ae_title"]["value"],\n        "query_retrieve": facts["pacs.query_retrieve.supported"]["value"],\n    }\n'''

    @staticmethod
    def _tests() -> str:
        return '''from fastapi.testclient import TestClient\n\nfrom app.main import app\n\n\ndef test_health():\n    response = TestClient(app).get("/health")\n    assert response.status_code == 200\n    assert response.json()["status"] == "ok"\n'''

    @staticmethod
    def _evidence() -> str:
        return (
            "# Evidence\n\n"
            "- Software search: Aygun et al., Nature 2026, "
            "doi:10.1038/s41586-026-10658-6\n"
            "- ERA reference implementation: https://github.com/google-research/era\n"
            "- Environment grounding: see docs/EVIDENCE_BASE.md in Project Vulcan.\n"
        )


class ObjectiveEvaluator:
    """Objective, fail-closed scoring. Generated code is compiled, not executed."""

    def __init__(self):
        self.environment_gate = EnvironmentGate()

    @staticmethod
    def _syntax(files: dict[str, str]) -> float:
        try:
            for path, source in files.items():
                if path.endswith(".py"):
                    compile(source, path, "exec")
        except SyntaxError:
            return 0.0
        return 1.0

    @staticmethod
    def _required_files(task: EvolutionTask) -> list[str]:
        required = ["environment.json", "APP_SPEC.md", "app/main.py", "tests/test_contract.py"]
        text = task.need.lower()
        if "fhir" in text or "ehr" in text:
            required.append("app/integrations/fhir.py")
        if any(term in text for term in ["image", "oct", "fundus", "pacs", "dicom"]):
            required.append("app/integrations/dicom.py")
        return required

    @staticmethod
    def _no_invented_values(files: dict[str, str]) -> float:
        forbidden = ("TODO", "FIXME", "example.com", "127.0.0.1", "localhost")
        python = "\n".join(value for key, value in files.items() if key.endswith(".py"))
        return 0.0 if any(term in python for term in forbidden) else 1.0

    def __call__(self, task: EvolutionTask, candidate: CodingCandidate) -> CodingCandidate:
        candidate = candidate.model_copy(deep=True)
        readiness = self.environment_gate.evaluate(task.need, task.environment)
        required = self._required_files(task)
        coverage = sum(path in candidate.files for path in required) / len(required)
        syntax = self._syntax(candidate.files)
        no_guessing = self._no_invented_values(candidate.files)
        tests = 1.0 if "tests/test_contract.py" in candidate.files else 0.0
        evidence = 1.0 if "environment.json" in candidate.files else 0.0

        candidate.metrics = {
            "artifact_coverage": coverage,
            "python_syntax": syntax,
            "no_invented_endpoints": no_guessing,
            "tests_present": tests,
            "environment_embedded": evidence,
        }
        candidate.hard_gate_passed = readiness.ready and syntax == 1.0 and no_guessing == 1.0
        candidate.score = (
            0.40 * coverage
            + 0.20 * syntax
            + 0.15 * no_guessing
            + 0.15 * tests
            + 0.10 * evidence
        )
        if not candidate.hard_gate_passed:
            candidate.score = 0.0
            candidate.logs.append("Hard gate failed; score forced to zero.")
        return candidate


class VulcanEvolutionEngine:
    def __init__(self):
        self.compiler = IntentCompiler()
        self.environment_gate = EnvironmentGate()
        self.safety_gate = SafetyGate()
        self.coder = EvidenceGroundedCoder()
        self.evaluator = ObjectiveEvaluator()
        self.search = FlatUCBSearch(c_puct=1.0)

    def evolve(self, request: EvolutionRequest) -> EvolutionResult:
        readiness = self.environment_gate.evaluate(request.need, request.environment)
        if not readiness.ready:
            return EvolutionResult(
                environment_ready=False,
                readiness=readiness,
                blocked_reason="Required clinic facts are missing or unusable.",
            )

        specification = self.compiler.compile(request.need)
        findings, deployable = self.safety_gate.evaluate(specification)
        if not deployable:
            codes = ", ".join(finding.code for finding in findings)
            return EvolutionResult(
                environment_ready=True,
                readiness=readiness,
                blocked_reason=f"SafetyGate blocked software evolution: {codes}",
            )

        task = EvolutionTask(request.need, request.environment, specification)
        seed = self.coder.seed(task)
        trace = self.search.run(
            task=task,
            seed=seed,
            generate=self.coder,
            evaluate=self.evaluator,
            iterations=request.iterations,
        )
        best = max(trace, key=lambda candidate: candidate.score)
        return EvolutionResult(
            environment_ready=True,
            readiness=readiness,
            best_candidate=best,
            candidates_evaluated=len(trace),
            search_trace=trace,
        )
