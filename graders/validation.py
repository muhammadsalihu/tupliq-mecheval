"""
Grader Validation Framework for MechEval.
Verifies that graders accept valid reference solutions, accept near-boundary answers within tolerance,
and deterministically reject common LLM physical failure modes.
"""

from typing import Dict, Any, List, Callable
from tasks.base import BaseTask


class GraderValidationSuite:
    def __init__(self, task: BaseTask):
        self.task = task
        self.ref = task.get_reference_solution()
        self.grader = task.get_grader()

    def test_reference_passes(self) -> bool:
        """The ground truth reference solution MUST achieve 100% pass."""
        report = self.grader.grade(self.ref, self.ref)
        if not report.all_passed or report.score < 1.0:
            raise AssertionError(f"Reference solution failed its own grader: {report.failure_reasons}")
        return True

    def test_within_tolerance_passes(self, perturbation: float = 0.005) -> bool:
        """Slight numerical rounding (e.g. 0.5% perturbation) should pass 1% tolerance."""
        perturbed = {}
        for k, v in self.ref.items():
            # If parameter is binary or int-like (e.g. 0 or 1), do not scale by percentage
            if isinstance(v, (int, bool)) or (isinstance(v, float) and v in (0.0, 1.0) and "is_" in k):
                perturbed[k] = v
            else:
                perturbed[k] = v * (1.0 + perturbation)
        report = self.grader.grade(perturbed, self.ref)
        if not report.all_passed:
            raise AssertionError(
                f"Candidate within tolerance (perturbed by {perturbation:.2%}) was falsely rejected: {report.failure_reasons}"
            )
        return True

    def test_exceeding_tolerance_fails(self, perturbation: float = 0.02) -> bool:
        """Candidate exceeding tolerance (e.g. 2.0% perturbation) must fail 1% tolerance."""
        perturbed = {}
        for k, v in self.ref.items():
            if isinstance(v, (int, bool)) or (isinstance(v, float) and v in (0.0, 1.0) and "is_" in k):
                perturbed[k] = v
            else:
                perturbed[k] = v * (1.0 + perturbation)
        report = self.grader.grade(perturbed, self.ref)
        if report.all_passed:
            raise AssertionError(
                f"Candidate exceeding tolerance ({perturbation:.2%}) falsely passed grader!"
            )
        return True

    def test_failure_mode(self, name: str, candidate_dict: Dict[str, Any]) -> bool:
        """A specific engineering bug must be rejected and flagged."""
        report = self.grader.grade(candidate_dict, self.ref)
        if report.all_passed:
            raise AssertionError(f"Deliberate failure mode '{name}' unexpectedly PASSED the grader!")
        return True
