"""
Unit tests and grader validation for Task 004: Thermal Expansion with Clearance Gap.
"""

import pytest
from tasks.task_004_thermal.task import ThermalExpansionGapTask
from graders.validation import GraderValidationSuite


def test_reference_solution_physical_sanity():
    """Verify calculated physical values against manual engineering hand calculation."""
    task = ThermalExpansionGapTask()
    ref = task.get_reference_solution()

    # Manual checks:
    # L = 1.5 m, alpha = 17.3e-6, delta T = 90 C
    # delta_L_free = 17.3e-6 * 1.5 * 90 = 2.3355 mm
    # delta_T_close = 0.00120 / (17.3e-6 * 1.5) = 46.2428 C
    # T_close = 20 + 46.2428 = 66.2428 C
    # delta_restrained = 2.3355 - 1.20 = 1.1355 mm
    # actual elongation = 1.20 mm
    # strain = 1.1355e-3 / 1.5 = 7.57e-4
    # sigma = 193e9 * 7.57e-4 = 146.099 MPa
    # Area = 0.04 * 0.04 = 0.0016 m^2
    # Reaction force = 146.099e6 * 0.0016 = 233,758.4 N

    assert pytest.approx(ref["free_thermal_expansion_mm"], rel=1e-3) == 2.3355
    assert pytest.approx(ref["temperature_to_close_gap_C"], rel=1e-3) == 66.243
    assert pytest.approx(ref["actual_elongation_mm"], rel=1e-4) == 1.200
    assert pytest.approx(ref["restrained_expansion_mm"], rel=1e-3) == 1.1355
    assert pytest.approx(ref["thermal_stress_MPa"], rel=1e-3) == 146.10
    assert pytest.approx(ref["reaction_force_N"], rel=1e-3) == 233758.4


def test_grader_accepts_reference_solution():
    task = ThermalExpansionGapTask()
    suite = GraderValidationSuite(task)
    assert suite.test_reference_passes() is True


def test_grader_tolerance_boundaries():
    task = ThermalExpansionGapTask()
    suite = GraderValidationSuite(task)
    assert suite.test_within_tolerance_passes(perturbation=0.005) is True
    assert suite.test_exceeding_tolerance_fails(perturbation=0.02) is True


def test_grader_rejects_zero_gap_assumption():
    """LLM Failure Mode 1: Model completely ignores clearance gap and computes full E*alpha*deltaT (300.5 MPa)."""
    task = ThermalExpansionGapTask()
    ref = task.get_reference_solution()
    zero_gap = dict(ref)
    zero_gap["thermal_stress_MPa"] = (task.elastic_modulus_GPa * 1e9 * task.thermal_expansion_coeff * (task.final_temp_C - task.initial_temp_C)) / 1e6
    zero_gap["reaction_force_N"] = zero_gap["thermal_stress_MPa"] * 1e6 * (task.width_m * task.height_m)

    report = task.grade(zero_gap)
    assert not report.all_passed
    assert "thermal_stress_MPa" in " ".join(report.failure_reasons)


def test_grader_rejects_rigid_stop_penetration():
    """LLM Failure Mode 2: Model claims actual elongation equals free thermal expansion (2.3355 mm instead of 1.20 mm)."""
    task = ThermalExpansionGapTask()
    ref = task.get_reference_solution()
    penetration = dict(ref)
    penetration["actual_elongation_mm"] = ref["free_thermal_expansion_mm"]  # Violates rigid boundary

    report = task.grade(penetration)
    assert not report.all_passed
    assert "actual_elongation_mm" in " ".join(report.failure_reasons)


def test_grader_rejects_delta_T_as_absolute_temp():
    """LLM Failure Mode 3: Model returns temperature rise (46.24 C) instead of absolute temperature (66.24 C)."""
    task = ThermalExpansionGapTask()
    ref = task.get_reference_solution()
    temp_blunder = dict(ref)
    temp_blunder["temperature_to_close_gap_C"] = ref["temperature_to_close_gap_C"] - task.initial_temp_C  # 46.24 C instead of 66.24 C

    report = task.grade(temp_blunder)
    assert not report.all_passed
    assert "temperature_to_close_gap_C" in " ".join(report.failure_reasons)
