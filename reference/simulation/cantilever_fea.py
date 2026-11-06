"""
Direct Stiffness Finite Element Method (1D Euler-Bernoulli Beam)
Numerical simulation reference for cantilever beam analysis.
Discretizes beam into N 2-node beam elements (2 DOFs per node: transverse deflection w, rotation theta).
"""

from typing import Dict, Any, Tuple
import numpy as np


def solve_cantilever_fem(
    length_m: float,
    width_m: float,
    height_m: float,
    elastic_modulus_GPa: float,
    density_kg_m3: float,
    tip_load_N: float,
    gravity_m_s2: float = 9.81,
    num_elements: int = 20,
) -> Dict[str, Any]:
    """
    Finite element solver using Hermite cubic interpolation Euler-Bernoulli beam elements.
    Includes consistent nodal load vector for uniform self-weight and point load at tip.
    """
    L = length_m
    b = width_m
    h = height_m
    E = elastic_modulus_GPa * 1e9
    rho = density_kg_m3
    P = tip_load_N
    g = gravity_m_s2

    A = b * h
    I = (b * (h ** 3)) / 12.0
    w0 = rho * g * A  # N/m downward

    num_nodes = num_elements + 1
    total_dofs = num_nodes * 2
    le = L / num_elements

    # Global stiffness matrix K and force vector F
    K_global = np.zeros((total_dofs, total_dofs))
    F_global = np.zeros(total_dofs)

    # Element stiffness matrix for 2-node Euler-Bernoulli beam
    k_e = (E * I / (le ** 3)) * np.array([
        [12.0,       6.0 * le,      -12.0,       6.0 * le],
        [6.0 * le,   4.0 * le**2,   -6.0 * le,   2.0 * le**2],
        [-12.0,     -6.0 * le,       12.0,      -6.0 * le],
        [6.0 * le,   2.0 * le**2,   -6.0 * le,   4.0 * le**2]
    ])

    # Consistent load vector for uniform downward load w0
    # Note: w0 acts in negative y direction, but we define w as positive downward for deflection
    f_e = (w0 * le / 12.0) * np.array([
        6.0,
        le,
        6.0,
        -le
    ])

    # Assembly
    for e in range(num_elements):
        dofs = [2 * e, 2 * e + 1, 2 * (e + 1), 2 * (e + 1) + 1]
        for i in range(4):
            F_global[dofs[i]] += f_e[i]
            for j in range(4):
                K_global[dofs[i], dofs[j]] += k_e[i, j]

    # Add tip point load at the last transverse DOF (node N, dof = 2*num_elements)
    F_global[2 * num_elements] += P

    # Boundary conditions: Clamped at x = 0 (node 0: dof 0 = 0, dof 1 = 0)
    # Partition system to solve for free DOFs
    free_dofs = np.arange(2, total_dofs)
    K_ff = K_global[np.ix_(free_dofs, free_dofs)]
    F_f = F_global[free_dofs]

    U_f = np.linalg.solve(K_ff, F_f)

    U_full = np.zeros(total_dofs)
    U_full[free_dofs] = U_f

    # Support reactions at fixed node 0
    R_reactions = K_global[:2, :] @ U_full - F_global[:2]
    R_y_N = R_reactions[0]
    M_root_Nm = R_reactions[1]

    # Tip deflection (DOF 2*num_elements)
    tip_deflection_m = U_full[2 * num_elements]
    tip_deflection_mm = tip_deflection_m * 1000.0

    # Max bending stress at root: sigma = M * (h/2) / I = M / Z
    Z = (b * (h ** 2)) / 6.0
    sigma_max_MPa = (abs(M_root_Nm) / Z) / 1e6
    tau_max_MPa = 1.5 * (abs(R_y_N) / A) / 1e6

    return {
        "num_elements": num_elements,
        "tip_deflection_mm": tip_deflection_mm,
        "support_reaction_N": abs(R_y_N),
        "root_bending_moment_Nm": abs(M_root_Nm),
        "max_bending_stress_MPa": sigma_max_MPa,
        "max_shear_stress_MPa": tau_max_MPa,
    }


if __name__ == "__main__":
    fem_res = solve_cantilever_fem(2.5, 0.06, 0.12, 210.0, 7850.0, 6500.0)
    print("FEM 20-element result:", fem_res)
