"""
Reference Analytical Solution for Task 004: Constrained Thermal Expansion With Pre-existing Gap.
Independently checked using thermo-elasticity and piecewise constraint formulation.
"""

from typing import Dict, Any


def solve_thermal_expansion_gap(
    length_m: float,
    width_m: float,
    height_m: float,
    elastic_modulus_GPa: float,
    thermal_expansion_coeff: float,  # 1/C
    initial_temp_C: float,
    final_temp_C: float,
    clearance_gap_m: float,
) -> Dict[str, Any]:
    """
    Computes exact thermal expansion, contact threshold, constrained mechanical stress,
    reaction force, and actual elongation for a bar expanding against a rigid stop with a gap.
    """
    L = length_m
    b = width_m
    h = height_m
    A = b * h
    E = elastic_modulus_GPa * 1e9
    alpha = thermal_expansion_coeff
    delta_0 = clearance_gap_m
    delta_T = final_temp_C - initial_temp_C

    # 1. Unconstrained free thermal expansion
    delta_L_free_m = alpha * L * delta_T
    delta_L_free_mm = delta_L_free_m * 1000.0

    # 2. Temperature rise to close gap exactly
    delta_T_close = delta_0 / (alpha * L)
    T_close_C = initial_temp_C + delta_T_close

    # 3. Check if gap is closed
    if delta_L_free_m <= delta_0:
        # Gap does not close; zero stress develops
        gap_closed = False
        delta_L_actual_mm = delta_L_free_mm
        sigma_thermal_MPa = 0.0
        reaction_force_N = 0.0
        restrained_expansion_mm = 0.0
    else:
        # Gap closes; rigid stop restricts further expansion
        gap_closed = True
        delta_L_actual_mm = delta_0 * 1000.0
        delta_restrained_m = delta_L_free_m - delta_0
        restrained_expansion_mm = delta_restrained_m * 1000.0
        
        # Mechanical compressive strain
        mech_strain = delta_restrained_m / L
        # Compressive thermal stress (magnitude)
        sigma_thermal_Pa = E * mech_strain
        sigma_thermal_MPa = sigma_thermal_Pa / 1e6
        # Reaction force at stop
        reaction_force_N = sigma_thermal_Pa * A

    return {
        "free_thermal_expansion_mm": delta_L_free_mm,
        "temperature_to_close_gap_C": T_close_C,
        "actual_elongation_mm": delta_L_actual_mm,
        "restrained_expansion_mm": restrained_expansion_mm,
        "thermal_stress_MPa": sigma_thermal_MPa,
        "reaction_force_N": reaction_force_N,
    }


if __name__ == "__main__":
    res = solve_thermal_expansion_gap(
        length_m=1.50,
        width_m=0.040,
        height_m=0.040,
        elastic_modulus_GPa=193.0,
        thermal_expansion_coeff=17.3e-6,
        initial_temp_C=20.0,
        final_temp_C=110.0,
        clearance_gap_m=0.00120,
    )
    print("Thermal Expansion Result:", res)
