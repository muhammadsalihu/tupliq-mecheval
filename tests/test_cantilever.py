"""
Unit tests and grader validation for Task 001: Cantilever Beam Analysis.
"""

import pytest
from tasks.task_001_cantilever.task import CantileverBeamTask
from reference.analytical.cantilever import verify_symbolic_cantilever, solve_cantilever_analytical
from graders.validation import GraderValidationSuite


def test_symbolic_cantilever_mechanics():
    """Verify governing Euler-Bernoulli beam differential equations symbolically."""
    assert verify_symbolic_cantilever() is True


def test_reference_solution_physical_sanity():
    """Verify calculated physical quantities match manual engineering hand calculation."""
    task = CantileverBeamTask()
    ref = task.get_reference_solution()

    # Manual checks for L=2.5, b=0.06, h=0.12, E=210 GPa, rho=7850 kg/m3, P=6500 N, g=9.81
    # Area = 0.06 * 0.12 = 0.0072 m^2
    # I = 0.06 * (0.12)^3 / 12 = 8.64e-6 m^4
    # Z = 0.06 * (0.12)^2 / 6 = 1.44e-4 m^3
    # w0 = 7850 * 9.81 * 0.0072 = 554.4612 N/m
    # Total w0*L = 1386.153 N
    # Support reaction Ry = 6500 + 1386.153 = 7886.153 N
    # M_root = 6500 * 2.5 + 554.4612 * 6.25 / 2 = 16250 + 1732.69125 = 17982.69125 N*m
    # sigma_max = 17982.69125 / 1.44e-4 = 124.8798 MPa
    # tau_max = 1.5 * 7886.153 / 0.0072 = 1.6429 MPa
    # delta_tip = P*L^3/(3EI) + w0*L^4/(8EI) = 18.667 mm + 1.488 mm = 20.155 mm

    assert pytest.approx(ref["second_moment_of_area_m4"], rel=1e-5) == 8.64e-6
    assert pytest.approx(ref["section_modulus_m3"], rel=1e-5) == 1.44e-4
    assert pytest.approx(ref["support_reaction_N"], rel=1e-4) == 7886.153
    assert pytest.approx(ref["root_bending_moment_Nm"], rel=1e-4) == 17982.691
    assert pytest.approx(ref["max_bending_stress_MPa"], rel=1e-3) == 124.88
    assert pytest.approx(ref["max_shear_stress_MPa"], rel=1e-3) == 1.643
    assert pytest.approx(ref["tip_deflection_mm"], rel=1e-3) == 20.155


def test_grader_accepts_reference_solution():
    """Ensure grader accepts exact reference solution with score 1.0."""
    task = CantileverBeamTask()
    suite = GraderValidationSuite(task)
    assert suite.test_reference_passes() is True


def test_grader_tolerance_boundaries():
    """Ensure grader accepts 0.5% perturbation and rejects 2.0% perturbation."""
    task = CantileverBeamTask()
    suite = GraderValidationSuite(task)
    assert suite.test_within_tolerance_passes(perturbation=0.005) is True
    assert suite.test_exceeding_tolerance_fails(perturbation=0.02) is True


def test_grader_rejects_omitted_self_weight():
    """LLM Failure Mode 1: Model completely neglects beam self-weight (P only)."""
    task = CantileverBeamTask()
    suite = GraderValidationSuite(task)

    # Solution neglecting self-weight (w0 = 0)
    w0_omitted = solve_cantilever_analytical(
        length_m=task.length_m,
        width_m=task.width_m,
        height_m=task.height_m,
        elastic_modulus_GPa=task.elastic_modulus_GPa,
        density_kg_m3=0.0,  # Zero density / zero self-weight
        tip_load_N=task.tip_load_N,
        gravity_m_s2=task.gravity_m_s2,
    )
    report = task.grade(w0_omitted)
    assert not report.all_passed
    assert "root_bending_moment_Nm" in " ".join(report.failure_reasons)
    assert "tip_deflection_mm" in " ".join(report.failure_reasons)


def test_grader_rejects_inverted_axis():
    """LLM Failure Mode 2: Model swaps base and height in inertia (weak axis bending)."""
    task = CantileverBeamTask()
    # Inverted axis: I = h * b^3 / 12
    ref = task.get_reference_solution()
    inverted = dict(ref)
    inverted["second_moment_of_area_m4"] = (task.height_m * (task.width_m ** 3)) / 12.0
    inverted["section_modulus_m3"] = (task.height_m * (task.width_m ** 2)) / 6.0
    inverted["max_bending_stress_MPa"] = ref["root_bending_moment_Nm"] / (inverted["section_modulus_m3"] * 1e6)

    report = task.grade(inverted)
    assert not report.all_passed
    assert "second_moment_of_area_m4" in " ".join(report.failure_reasons)


def test_grader_rejects_unit_conversion_blunder():
    """LLM Failure Mode 3: Model returns stress in Pascals instead of requested MPa (off by 10^6)."""
    task = CantileverBeamTask()
    ref = task.get_reference_solution()
    unit_blunder = dict(ref)
    unit_blunder["max_bending_stress_MPa"] = ref["max_bending_stress_MPa"] * 1e6  # Outputting in Pa

    report = task.grade(unit_blunder)
    assert not report.all_passed
    assert "max_bending_stress_MPa" in " ".join(report.failure_reasons)


def test_grader_rejects_simply_supported_deflection_formula():
    """LLM Failure Mode 4: Model confuses cantilever formula (PL^3/3EI) with simply supported beam (PL^3/48EI)."""
    task = CantileverBeamTask()
    ref = task.get_reference_solution()
    formula_confusion = dict(ref)
    # Using PL^3/(48EI)
    L, E, I, P = task.length_m, task.elastic_modulus_GPa * 1e9, ref["second_moment_of_area_m4"], task.tip_load_N
    formula_confusion["tip_deflection_mm"] = (P * L**3 / (48 * E * I)) * 1000.0

    report = task.grade(formula_confusion)
    assert not report.all_passed
    assert "tip_deflection_mm" in " ".join(report.failure_reasons)


def test_fem_simulation_agreement():
    """Verify that independent numerical FEM simulation matches analytical reference to < 0.01%."""
    from reference.simulation.cantilever_fea import solve_cantilever_fem
    task = CantileverBeamTask()
    analytical_ref = task.get_reference_solution()
    fem_ref = solve_cantilever_fem(
        length_m=task.length_m,
        width_m=task.width_m,
        height_m=task.height_m,
        elastic_modulus_GPa=task.elastic_modulus_GPa,
        density_kg_m3=task.density_kg_m3,
        tip_load_N=task.tip_load_N,
        gravity_m_s2=task.gravity_m_s2,
        num_elements=20,
    )
    # Check agreement between analytical and numerical simulation
    assert pytest.approx(fem_ref["tip_deflection_mm"], rel=1e-4) == analytical_ref["tip_deflection_mm"]
    assert pytest.approx(fem_ref["support_reaction_N"], rel=1e-4) == analytical_ref["support_reaction_N"]
    assert pytest.approx(fem_ref["root_bending_moment_Nm"], rel=1e-4) == analytical_ref["root_bending_moment_Nm"]
    assert pytest.approx(fem_ref["max_bending_stress_MPa"], rel=1e-4) == analytical_ref["max_bending_stress_MPa"]

