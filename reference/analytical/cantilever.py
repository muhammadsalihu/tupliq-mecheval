"""
Reference Analytical Solution for Task 001: Cantilever Beam Analysis.
Independently checked using SymPy symbolic integration and exact mechanics of materials.
"""

from typing import Dict, Any
import sympy as sp


def solve_cantilever_analytical(
    length_m: float,
    width_m: float,
    height_m: float,
    elastic_modulus_GPa: float,
    density_kg_m3: float,
    tip_load_N: float,
    gravity_m_s2: float = 9.81,
) -> Dict[str, Any]:
    """
    Computes exact closed-form mechanics solution for a cantilever beam
    subjected to tip point load P and distributed self-weight w0 = rho * g * b * h.
    """
    # Convert inputs to standard SI units
    L = length_m
    b = width_m
    h = height_m
    E = elastic_modulus_GPa * 1e9  # GPa to Pa
    rho = density_kg_m3
    P = tip_load_N
    g = gravity_m_s2

    # Cross section geometry
    A = b * h
    I = (b * (h ** 3)) / 12.0
    Z = (b * (h ** 2)) / 6.0

    # Self-weight distributed load per unit length (N/m)
    w0 = rho * g * A

    # Support reaction force at root x = 0
    R_y = P + w0 * L

    # Maximum bending moment occurs at the fixed root x = 0
    M_root = P * L + (w0 * (L ** 2)) / 2.0

    # Maximum bending stress (at outermost fiber y = h/2 at root)
    sigma_max_Pa = M_root / Z
    sigma_max_MPa = sigma_max_Pa / 1e6

    # Maximum transverse shear stress (at neutral axis of rectangular section)
    tau_max_Pa = 1.5 * (R_y / A)
    tau_max_MPa = tau_max_Pa / 1e6

    # Tip deflection delta_tip (superposition of point load and uniform self-weight)
    # delta_P = P * L^3 / (3 * E * I)
    # delta_w = w0 * L^4 / (8 * E * I)
    delta_tip_m = (P * (L ** 3)) / (3.0 * E * I) + (w0 * (L ** 4)) / (8.0 * E * I)
    delta_tip_mm = delta_tip_m * 1000.0

    return {
        "second_moment_of_area_m4": I,
        "section_modulus_m3": Z,
        "support_reaction_N": R_y,
        "root_bending_moment_Nm": M_root,
        "max_bending_stress_MPa": sigma_max_MPa,
        "max_shear_stress_MPa": tau_max_MPa,
        "tip_deflection_mm": delta_tip_mm,
    }


def verify_symbolic_cantilever():
    """
    Symbolically derives and verifies the governing equations via differential equations:
    EI * d^4 w / dx^4 = -w0
    Subject to:
    w(0) = 0
    w'(0) = 0
    w''(L) = 0
    w'''(L) = P / (E*I)
    """
    x = sp.Symbol('x', positive=True)
    L, E, I, P, w0 = sp.symbols('L E I P w0', positive=True)

    # Deflection curve w(x)
    # Direct integration of bending moment:
    # M(x) = P*(L - x) + w0*(L - x)^2 / 2
    M_x = P * (L - x) + (w0 * (L - x)**2) / 2
    
    # Root moment at x = 0
    M_0 = M_x.subs(x, 0)
    expected_M0 = P * L + (w0 * L**2) / 2
    assert sp.simplify(M_0 - expected_M0) == 0, "Root moment symbolic check failed"

    # Slope theta(x) = int(M(x)/(E*I), x) + C1, with theta(0) = 0
    theta_x = sp.integrate(M_x / (E * I), x)
    C1 = -theta_x.subs(x, 0)
    theta_x = theta_x + C1

    # Deflection w(x) = int(theta(x), x) + C2, with w(0) = 0
    w_x = sp.integrate(theta_x, x)
    C2 = -w_x.subs(x, 0)
    w_x = sp.simplify(w_x + C2)

    # Tip deflection at x = L
    w_tip = sp.simplify(w_x.subs(x, L))
    expected_w_tip = (P * L**3) / (3 * E * I) + (w0 * L**4) / (8 * E * I)
    assert sp.simplify(w_tip - expected_w_tip) == 0, "Tip deflection symbolic derivation check failed"
    return True


if __name__ == "__main__":
    verify_symbolic_cantilever()
    res = solve_cantilever_analytical(
        length_m=2.0,
        width_m=0.05,
        height_m=0.10,
        elastic_modulus_GPa=200.0,
        density_kg_m3=7850.0,
        tip_load_N=5000.0,
    )
    print("Analytical Cantilever Results:", res)
