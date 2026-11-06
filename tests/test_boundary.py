"""
Unit tests and grader validation for Task 003: Indeterminate Propped Cantilever.
"""

import pytest
from tasks.task_003_boundary.task import ProppedCantileverTask
from reference.analytical.boundary import verify_symbolic_propped_cantilever
from graders.validation import GraderValidationSuite


def test_symbolic_propped_cantilever():
    """Verify symbolic compatibility derivation."""
    assert verify_symbolic_propped_cantilever() is True


def test_reference_solution_physical_sanity():
    """Verify physical quantities match manual engineering hand calculation."""
    task = ProppedCantileverTask()
    ref = task.get_reference_solution()

    # w = 12,000 N/m, L = 4.0 m
    # w*L = 48,000 N
    # R_B = 3/8 * 48,000 = 18,000 N
    # R_A = 5/8 * 48,000 = 30,000 N
    # M_A = 1/8 * 12,000 * 16 = 24,000 N*m
    # x_max_pos = 5/8 * 4 = 2.5 m
    # M_pos_max = 9/128 * 12,000 * 16 = 13,500 N*m
    # x_contraflexure = 4.0 / 4 = 1.0 m
    # I = 0.1 * 0.2^3 / 12 = 6.66667e-5 m^4
    # Z = 0.1 * 0.2^2 / 6 = 6.66667e-4 m^3
    # max bending stress = 24,000 / 6.66667e-4 = 36.0 MPa

    assert pytest.approx(ref["roller_reaction_N"], rel=1e-4) == 18000.0
    assert pytest.approx(ref["wall_vertical_reaction_N"], rel=1e-4) == 30000.0
    assert pytest.approx(ref["wall_moment_Nm"], rel=1e-4) == 24000.0
    assert pytest.approx(ref["x_max_positive_moment_m"], rel=1e-4) == 2.50
    assert pytest.approx(ref["max_positive_moment_Nm"], rel=1e-4) == 13500.0
    assert pytest.approx(ref["x_contraflexure_m"], rel=1e-4) == 1.00
    assert pytest.approx(ref["max_bending_stress_MPa"], rel=1e-3) == 36.0


def test_grader_accepts_reference_solution():
    task = ProppedCantileverTask()
    suite = GraderValidationSuite(task)
    assert suite.test_reference_passes() is True


def test_grader_tolerance_boundaries():
    task = ProppedCantileverTask()
    suite = GraderValidationSuite(task)
    assert suite.test_within_tolerance_passes(perturbation=0.005) is True
    assert suite.test_exceeding_tolerance_fails(perturbation=0.02) is True


def test_grader_rejects_simply_supported_reaction_hallucination():
    """LLM Failure Mode: Model ignores wall moment and guesses simply supported reactions (R_A = R_B = wL/2 = 24 kN)."""
    task = ProppedCantileverTask()
    ref = task.get_reference_solution()
    hallucinated = dict(ref)
    hallucinated["roller_reaction_N"] = 24000.0  # 33% error
    hallucinated["wall_vertical_reaction_N"] = 24000.0  # 20% error

    report = task.grade(hallucinated)
    assert not report.all_passed
    assert "roller_reaction_N" in " ".join(report.failure_reasons)


def test_grader_rejects_contraflexure_guess():
    """LLM Failure Mode: Model guesses midspan x = L/2 = 2.0 m for contraflexure instead of solving M(x)=0 (x = 1.0 m)."""
    task = ProppedCantileverTask()
    ref = task.get_reference_solution()
    bad_inflect = dict(ref)
    bad_inflect["x_contraflexure_m"] = 2.00  # 100% error!

    report = task.grade(bad_inflect)
    assert not report.all_passed
    assert "x_contraflexure_m" in " ".join(report.failure_reasons)


def test_grader_rejects_fixed_fixed_moment_formula():
    """LLM Failure Mode: Model confuses propped cantilever with fixed-fixed beam (M_A = wL^2/12 = 16,000 N*m)."""
    task = ProppedCantileverTask()
    ref = task.get_reference_solution()
    fixed_fixed = dict(ref)
    fixed_fixed["wall_moment_Nm"] = (12000.0 * 16.0) / 12.0  # 16,000 N*m instead of 24,000 N*m (33% error)

    report = task.grade(fixed_fixed)
    assert not report.all_passed
    assert "wall_moment_Nm" in " ".join(report.failure_reasons)
