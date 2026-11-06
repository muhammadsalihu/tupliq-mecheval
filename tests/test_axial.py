"""
Unit tests and grader validation for Task 002: Stepped Axial Bar.
"""

import pytest
import math
from tasks.task_002_axial.task import SteppedAxialBarTask
from reference.analytical.axial import solve_stepped_axial_bar
from graders.validation import GraderValidationSuite


def test_reference_solution_physical_sanity():
    """Verify calculated physical quantities match manual engineering hand calculation."""
    task = SteppedAxialBarTask()
    ref = task.get_reference_solution()

    # Manual sanity check:
    # A1 = pi * (0.05)^2 / 4 = 1.963495e-3 m^2
    # A2 = pi * (0.03)^2 / 4 = 7.068583e-4 m^2
    # N2 = 80,000 N
    # N1 = 80,000 - 45,000 = 35,000 N
    # R_wall = 35,000 N
    # sigma1 = 35000 / 1.963495e-3 = 17.825 MPa
    # sigma2 = 80000 / 7.068583e-4 = 113.177 MPa
    # delta1 = (35000 * 1.2) / (1.963495e-3 * 70e9) = 0.30558 mm
    # delta2 = (80000 * 0.8) / (7.068583e-4 * 200e9) = 0.45271 mm
    # tip_deflection = 0.30558 + 0.45271 = 0.75829 mm
    # strain energy U = 0.5 * 35000 * 0.30558e-3 + 0.5 * 80000 * 0.45271e-3 = 5.348 + 18.108 = 23.456 J

    assert pytest.approx(ref["normal_force_seg1_N"], rel=1e-4) == 35000.0
    assert pytest.approx(ref["normal_force_seg2_N"], rel=1e-4) == 80000.0
    assert pytest.approx(ref["wall_reaction_N"], rel=1e-4) == 35000.0
    assert pytest.approx(ref["stress_seg1_MPa"], rel=1e-3) == 17.825
    assert pytest.approx(ref["stress_seg2_MPa"], rel=1e-3) == 113.177
    assert pytest.approx(ref["elongation_seg1_mm"], rel=1e-3) == 0.3056
    assert pytest.approx(ref["elongation_seg2_mm"], rel=1e-3) == 0.4527
    assert pytest.approx(ref["tip_deflection_mm"], rel=1e-3) == 0.7583
    assert pytest.approx(ref["strain_energy_J"], rel=1e-3) == 23.456


def test_grader_accepts_reference_solution():
    task = SteppedAxialBarTask()
    suite = GraderValidationSuite(task)
    assert suite.test_reference_passes() is True


def test_grader_tolerance_boundaries():
    task = SteppedAxialBarTask()
    suite = GraderValidationSuite(task)
    assert suite.test_within_tolerance_passes(perturbation=0.005) is True
    assert suite.test_exceeding_tolerance_fails(perturbation=0.02) is True


def test_grader_rejects_sign_error_on_intermediate_load():
    """LLM Failure Mode: Model adds intermediate load instead of subtracting (N1 = 80 + 45 = 125 kN)."""
    task = SteppedAxialBarTask()
    ref = task.get_reference_solution()
    sign_error = dict(ref)
    sign_error["normal_force_seg1_N"] = 125000.0
    sign_error["stress_seg1_MPa"] = 125000.0 / ((math.pi * task.diameter_1_m**2 / 4.0) * 1e6)
    sign_error["wall_reaction_N"] = 125000.0

    report = task.grade(sign_error)
    assert not report.all_passed
    assert "normal_force_seg1_N" in " ".join(report.failure_reasons)


def test_grader_rejects_ignored_intermediate_load():
    """LLM Failure Mode: Model assumes single tension force carries through entire bar (N1 = N2 = 80 kN)."""
    task = SteppedAxialBarTask()
    ref = task.get_reference_solution()
    ignored_int = dict(ref)
    ignored_int["normal_force_seg1_N"] = 80000.0
    ignored_int["wall_reaction_N"] = 80000.0
    ignored_int["stress_seg1_MPa"] = 80000.0 / ((math.pi * task.diameter_1_m**2 / 4.0) * 1e6)

    report = task.grade(ignored_int)
    assert not report.all_passed
    assert "normal_force_seg1_N" in " ".join(report.failure_reasons)


def test_grader_rejects_diameter_squared_area_blunder():
    """LLM Failure Mode: Model uses A = pi * d^2 instead of pi * d^2 / 4 (off by factor of 4)."""
    task = SteppedAxialBarTask()
    ref = task.get_reference_solution()
    area_blunder = dict(ref)
    area_blunder["stress_seg1_MPa"] = ref["stress_seg1_MPa"] / 4.0
    area_blunder["stress_seg2_MPa"] = ref["stress_seg2_MPa"] / 4.0
    area_blunder["tip_deflection_mm"] = ref["tip_deflection_mm"] / 4.0

    report = task.grade(area_blunder)
    assert not report.all_passed
    assert "stress_seg1_MPa" in " ".join(report.failure_reasons)
