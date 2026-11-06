"""
Unit tests and grader validation for Task 005: Mesh Convergence and Discretization Error.
"""

import pytest
from tasks.task_005_convergence.task import MeshConvergenceTask
from graders.validation import GraderValidationSuite


def test_reference_solution_physical_sanity():
    """Verify calculated verification quantities match manual calculation."""
    task = MeshConvergenceTask()
    ref = task.get_reference_solution()

    # Manual check:
    # diff_21 = 19.680 - 18.240 = 1.440
    # diff_32 = 20.040 - 19.680 = 0.360
    # ratio = 1.440 / 0.360 = 4.0
    # r = 2.0
    # p = ln(4) / ln(2) = 2.000
    # extrap = 20.040 + 0.360 / (2^2 - 1) = 20.040 + 0.120 = 20.160 mm
    # fine mesh error % = (0.120 / 20.160) * 100 = 0.595238 %
    # e32 = 0.360 / 20.040 = 0.01796407
    # GCI % = (1.25 * 0.01796407 / 3) * 100 = 0.748503 %
    # is_sharp_corner_singular = 1.0

    assert pytest.approx(ref["apparent_order_p"], rel=1e-3) == 2.000
    assert pytest.approx(ref["extrapolated_value"], rel=1e-3) == 20.160
    assert pytest.approx(ref["fine_mesh_discretization_error_percent"], rel=1e-3) == 0.5952
    assert pytest.approx(ref["grid_convergence_index_gci_percent"], rel=1e-3) == 0.7485
    assert ref["is_sharp_corner_singular"] == 1.0


def test_grader_accepts_reference_solution():
    task = MeshConvergenceTask()
    suite = GraderValidationSuite(task)
    assert suite.test_reference_passes() is True


def test_grader_tolerance_boundaries():
    task = MeshConvergenceTask()
    suite = GraderValidationSuite(task)
    assert suite.test_within_tolerance_passes(perturbation=0.005) is True
    assert suite.test_exceeding_tolerance_fails(perturbation=0.05) is True


def test_grader_rejects_singularity_misclassification():
    """LLM Failure Mode 1: Model claims sharp corner stress is physically converging (is_sharp_corner_singular = 0)."""
    task = MeshConvergenceTask()
    ref = task.get_reference_solution()
    misclassified = dict(ref)
    misclassified["is_sharp_corner_singular"] = 0.0  # False claim

    report = task.grade(misclassified)
    assert not report.all_passed
    assert "is_sharp_corner_singular" in " ".join(report.failure_reasons)


def test_grader_rejects_linear_extrapolation():
    """LLM Failure Mode 2: Model uses linear slope instead of asymptotic order p extrapolation."""
    task = MeshConvergenceTask()
    ref = task.get_reference_solution()
    linear = dict(ref)
    # Simple linear extrapolation from mesh 2 to mesh 3: f3 + (f3 - f2) = 20.040 + 0.360 = 20.400 mm
    linear["extrapolated_value"] = 20.400
    linear["apparent_order_p"] = 1.000

    report = task.grade(linear)
    assert not report.all_passed
    assert "extrapolated_value" in " ".join(report.failure_reasons)
