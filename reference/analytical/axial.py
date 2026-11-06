"""
Reference Analytical Solution for Task 002: Stepped Axial Bar Under Intermediate Loading.
Independently verified using method of sections, elasticity theory, and strain energy.
"""

from typing import Dict, Any
import math


def solve_stepped_axial_bar(
    length_1_m: float,
    diameter_1_m: float,
    elastic_modulus_1_GPa: float,
    length_2_m: float,
    diameter_2_m: float,
    elastic_modulus_2_GPa: float,
    intermediate_load_N: float,  # Directed toward wall (-x)
    end_load_N: float,           # Directed away from wall (+x)
) -> Dict[str, Any]:
    """
    Computes exact internal normal forces, stresses, elongations, and total tip deflection.
    Segment 1: [0, L1], fixed at x = 0.
    Intermediate load F_int at x = L1 pointing towards root (-x).
    Segment 2: [L1, L1 + L2].
    End load F_end at x = L1 + L2 pointing away from root (+x).
    """
    # Areas in m^2
    A1 = (math.pi * (diameter_1_m ** 2)) / 4.0
    A2 = (math.pi * (diameter_2_m ** 2)) / 4.0

    E1 = elastic_modulus_1_GPa * 1e9
    E2 = elastic_modulus_2_GPa * 1e9

    # Internal normal forces by method of sections:
    # Segment 2: Free-body cut between L1 and L1+L2
    # N2 = F_end
    N2 = end_load_N

    # Segment 1: Free-body cut between 0 and L1
    # N1 = F_end - F_int
    N1 = end_load_N - intermediate_load_N

    # Wall reaction force magnitude at x = 0
    R_wall = abs(N1)

    # Normal stresses in Pa and MPa
    sigma1_Pa = N1 / A1
    sigma2_Pa = N2 / A2
    sigma1_MPa = sigma1_Pa / 1e6
    sigma2_MPa = sigma2_Pa / 1e6

    # Elongations in meters and millimeters
    delta1_m = (N1 * length_1_m) / (A1 * E1)
    delta2_m = (N2 * length_2_m) / (A2 * E2)
    delta1_mm = delta1_m * 1000.0
    delta2_mm = delta2_m * 1000.0

    # Total elongation at the free tip x = L1 + L2
    delta_total_mm = delta1_mm + delta2_mm

    # Total elastic strain energy (Joules)
    strain_energy_J = (N1**2 * length_1_m) / (2.0 * A1 * E1) + (N2**2 * length_2_m) / (2.0 * A2 * E2)

    return {
        "normal_force_seg1_N": N1,
        "normal_force_seg2_N": N2,
        "wall_reaction_N": R_wall,
        "stress_seg1_MPa": sigma1_MPa,
        "stress_seg2_MPa": sigma2_MPa,
        "elongation_seg1_mm": delta1_mm,
        "elongation_seg2_mm": delta2_mm,
        "tip_deflection_mm": delta_total_mm,
        "strain_energy_J": strain_energy_J,
    }


if __name__ == "__main__":
    res = solve_stepped_axial_bar(
        length_1_m=1.20,
        diameter_1_m=0.050,
        elastic_modulus_1_GPa=70.0,
        length_2_m=0.80,
        diameter_2_m=0.030,
        elastic_modulus_2_GPa=200.0,
        intermediate_load_N=45000.0,
        end_load_N=80000.0,
    )
    print("Stepped Axial Bar Result:", res)
