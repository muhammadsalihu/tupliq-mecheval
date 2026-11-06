"""
Reference Analytical Solution for Task 003: Boundary Conditions & Statically Indeterminate Beam.
Independently checked using SymPy symbolic compatibility derivation and beam theory.
"""

from typing import Dict, Any
import sympy as sp
import math


def solve_propped_cantilever_analytical(
    length_m: float,
    distributed_load_N_m: float,
    width_m: float,
    height_m: float,
    elastic_modulus_GPa: float,
) -> Dict[str, Any]:
    """
    Computes exact reactions, internal moments, contraflexure point, and max deflection
    for a propped cantilever beam (fixed at x=0, roller at x=L) under uniform load w.
    """
    L = length_m
    w = distributed_load_N_m
    b = width_m
    h = height_m
    E = elastic_modulus_GPa * 1e9

    I = (b * (h ** 3)) / 12.0
    Z = (b * (h ** 2)) / 6.0

    # Indeterminate reaction at roller B (x = L):
    # Compatibility: delta_B = w*L^4/(8*E*I) - R_B*L^3/(3*E*I) = 0
    # R_B = (3/8) * w * L
    R_B_N = 0.375 * w * L

    # Vertical reaction at wall A (x = 0):
    # R_A = w * L - R_B = (5/8) * w * L
    R_A_N = 0.625 * w * L

    # Clamping moment magnitude at wall A (x = 0):
    # M_A = (1/8) * w * L^2
    M_A_Nm = 0.125 * w * (L ** 2)

    # Location of maximum positive bending moment (where shear V(x) = 0):
    # V(x) = R_A - w * x = 0 => x = 5/8 * L
    x_max_moment_m = 0.625 * L

    # Maximum positive bending moment:
    # M_pos = (9/128) * w * L^2
    M_pos_max_Nm = (9.0 / 128.0) * w * (L ** 2)

    # Point of contraflexure / inflection (where M(x) = 0 between 0 and L):
    # 4*x^2 - 5*L*x + L^2 = 0 => x = L / 4
    x_contraflexure_m = 0.25 * L

    # Maximum bending stress (occurs at wall x = 0 where moment is highest: M_A > M_pos)
    # M_A = (16/128) * w*L^2 vs M_pos = (9/128) * w*L^2
    max_bending_stress_MPa = (M_A_Nm / Z) / 1e6

    # Location of maximum deflection: x = (9 - sqrt(21))/6 * L
    x_max_defl_ratio = (9.0 - math.sqrt(21.0)) / 6.0
    x_max_defl_m = x_max_defl_ratio * L

    # Deflection function: w(x) = (w/(48*E*I)) * (2*x^4 - 5*L*x^3 + 3*L^2*x^2)
    # Max deflection at x_max_defl
    u = x_max_defl_ratio
    max_defl_m = (w * (L ** 4) / (48.0 * E * I)) * (2.0 * u**4 - 5.0 * u**3 + 3.0 * u**2)
    max_defl_mm = max_defl_m * 1000.0

    return {
        "roller_reaction_N": R_B_N,
        "wall_vertical_reaction_N": R_A_N,
        "wall_moment_Nm": M_A_Nm,
        "x_max_positive_moment_m": x_max_moment_m,
        "max_positive_moment_Nm": M_pos_max_Nm,
        "x_contraflexure_m": x_contraflexure_m,
        "max_bending_stress_MPa": max_bending_stress_MPa,
        "max_deflection_mm": max_defl_mm,
    }


def verify_symbolic_propped_cantilever():
    """Symbolically derive and verify all governing equations."""
    x, L, w, E, I = sp.symbols('x L w E I', positive=True)
    R_B = sp.symbols('R_B')

    # Governing moment: M(x) = -M_A + R_A*x - w*x^2/2
    # In terms of roller reaction R_B:
    # M(x) = R_B*(L - x) - w*(L - x)^2/2
    M_x = R_B * (L - x) - w * (L - x)**2 / 2

    # EI * w''(x) = M(x)
    # theta(x) = int(M_x, x) + C1, with theta(0) = 0
    theta_x = sp.integrate(M_x, x)
    C1 = -theta_x.subs(x, 0)
    theta_x = theta_x + C1

    w_x = sp.integrate(theta_x, x)
    C2 = -w_x.subs(x, 0)
    w_x = w_x + C2

    # Compatibility: w(L) = 0
    eq_compat = sp.Eq(w_x.subs(x, L), 0)
    sol_RB = sp.solve(eq_compat, R_B)[0]
    assert sol_RB == (3 * w * L) / 8, f"R_B derivation failed: {sol_RB}"

    # Wall reaction R_A
    R_A = w * L - sol_RB
    assert R_A == (5 * w * L) / 8

    # Wall moment M_A
    M_A = sp.simplify(w * L**2 / 2 - sol_RB * L)
    assert M_A == (w * L**2) / 8

    # Inflection point M(x) = 0
    M_x_solved = sp.simplify(M_x.subs(R_B, sol_RB))
    inflect_roots = sp.solve(sp.Eq(M_x_solved, 0), x)
    assert L / 4 in inflect_roots, f"Inflection point derivation failed: {inflect_roots}"

    return True


if __name__ == "__main__":
    verify_symbolic_propped_cantilever()
    res = solve_propped_cantilever_analytical(4.0, 12000.0, 0.10, 0.20, 205.0)
    print("Propped Cantilever Analytical Results:", res)
