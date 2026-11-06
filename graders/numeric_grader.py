"""
MechEval Numeric Grader
Deterministic grading functions with configurable absolute and relative tolerances.
"""

from typing import Union, Dict, Any, Tuple
import math

class NumericTolerance:
    def __init__(self, rel_tol: float = 0.01, abs_tol: float = 1e-6):
        """
        rel_tol: Relative tolerance (default 1% = 0.01)
        abs_tol: Absolute tolerance for near-zero values
        """
        self.rel_tol = rel_tol
        self.abs_tol = abs_tol

    def check(self, candidate: float, reference: float) -> Tuple[bool, float]:
        """
        Returns (passed: bool, relative_error: float)
        """
        if candidate is None or math.isnan(candidate) or math.isinf(candidate):
            return False, float("inf")
        
        # If reference is zero or extremely small, use absolute tolerance
        if abs(reference) < 1e-12:
            abs_err = abs(candidate - reference)
            passed = abs_err <= self.abs_tol
            return passed, abs_err

        rel_err = abs(candidate - reference) / abs(reference)
        passed = rel_err <= self.rel_tol
        return passed, rel_err


def grade_numeric_value(
    candidate: Any,
    reference: float,
    rel_tol: float = 0.01,
    abs_tol: float = 1e-6,
    param_name: str = "value",
) -> Dict[str, Any]:
    """
    Grades a single numeric parameter.
    """
    try:
        cand_float = float(candidate)
    except (ValueError, TypeError):
        return {
            "parameter": param_name,
            "passed": False,
            "candidate": candidate,
            "reference": reference,
            "error_type": "TYPE_CONVERSION_ERROR",
            "message": f"Could not convert candidate '{candidate}' to float.",
            "relative_error": None,
        }

    tol = NumericTolerance(rel_tol=rel_tol, abs_tol=abs_tol)
    passed, error = tol.check(cand_float, reference)

    return {
        "parameter": param_name,
        "passed": passed,
        "candidate": cand_float,
        "reference": reference,
        "relative_error": error,
        "rel_tol": rel_tol,
        "message": "Within tolerance" if passed else f"Exceeds tolerance (rel_error: {error:.4%}, allowed: {rel_tol:.2%})",
    }
