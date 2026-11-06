"""
MechEval Structured Simulation & Engineering Grader
Evaluates full engineering solutions against multi-field reference schemas.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from graders.numeric_grader import grade_numeric_value


class ParameterSpec(BaseModel):
    name: str
    description: str
    unit: str
    rel_tol: float = 0.01  # Default 1% tolerance
    abs_tol: float = 1e-6
    weight: float = 1.0


class GradingReport(BaseModel):
    task_id: str
    all_passed: bool
    score: float  # Weighted score [0.0, 1.0]
    total_weights: float
    passed_weights: float
    parameter_results: List[Dict[str, Any]]
    failure_reasons: List[str]
    raw_candidate: Optional[Dict[str, Any]] = None


class StructuredGrader:
    def __init__(self, task_id: str, specs: List[ParameterSpec]):
        self.task_id = task_id
        self.specs = specs

    def grade(
        self,
        candidate_dict: Dict[str, Any],
        reference_dict: Dict[str, Any]
    ) -> GradingReport:
        """
        Grades candidate solution dictionary against reference dictionary.
        """
        param_results = []
        failure_reasons = []
        total_weights = 0.0
        passed_weights = 0.0

        for spec in self.specs:
            total_weights += spec.weight
            if spec.name not in reference_dict:
                raise KeyError(f"Reference solution missing required parameter: {spec.name}")

            ref_val = reference_dict[spec.name]

            if candidate_dict is None or spec.name not in candidate_dict:
                param_results.append({
                    "parameter": spec.name,
                    "passed": False,
                    "candidate": None,
                    "reference": ref_val,
                    "unit": spec.unit,
                    "error_type": "MISSING_PARAMETER",
                    "message": f"Parameter '{spec.name}' was missing in candidate output.",
                    "relative_error": None,
                })
                failure_reasons.append(f"Missing parameter '{spec.name}'")
                continue

            cand_val = candidate_dict[spec.name]
            result = grade_numeric_value(
                candidate=cand_val,
                reference=ref_val,
                rel_tol=spec.rel_tol,
                abs_tol=spec.abs_tol,
                param_name=spec.name,
            )
            result["unit"] = spec.unit

            if result["passed"]:
                passed_weights += spec.weight
            else:
                failure_reasons.append(
                    f"{spec.name}: candidate={cand_val} {spec.unit}, "
                    f"reference={ref_val} {spec.unit} ({result['message']})"
                )

            param_results.append(result)

        score = passed_weights / total_weights if total_weights > 0 else 0.0
        all_passed = (len(failure_reasons) == 0)

        return GradingReport(
            task_id=self.task_id,
            all_passed=all_passed,
            score=score,
            total_weights=total_weights,
            passed_weights=passed_weights,
            parameter_results=param_results,
            failure_reasons=failure_reasons,
            raw_candidate=candidate_dict,
        )
