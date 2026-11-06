"""
Reference Analytical & Numerical Solution for Task 005: Mesh Convergence & Discretization Sanity.
Implements ASME V&V 20 / Richardson extrapolation and singularity classification.
"""

from typing import Dict, Any
import math


def solve_mesh_convergence(
    h1_mm: float,
    h2_mm: float,
    h3_mm: float,
    f1: float,
    f2: float,
    f3: float,
    safety_factor: float = 1.25,
) -> Dict[str, Any]:
    """
    Computes exact Richardson extrapolation, order of convergence p,
    fine-mesh relative error, and Grid Convergence Index (GCI) according to ASME V&V 20.
    h1 > h2 > h3 (coarse to fine).
    f1, f2, f3 are numerical solution values on meshes 1, 2, 3.
    """
    r21 = h1_mm / h2_mm
    r32 = h2_mm / h3_mm

    if abs(r21 - r32) > 1e-5:
        raise ValueError(f"Mesh refinement ratio must be uniform: r21={r21}, r32={r32}")

    r = r32

    # Step changes
    diff_21 = f2 - f1
    diff_32 = f3 - f2

    # Apparent order of convergence p
    ratio = diff_21 / diff_32
    if ratio <= 0:
        raise ValueError(f"Oscillatory or non-monotonic convergence: ratio={ratio}")
    p = math.log(ratio) / math.log(r)

    # Richardson extrapolation to h = 0
    f_extrap = f3 + diff_32 / (r**p - 1.0)

    # Relative error of fine mesh compared to extrapolated continuum value
    rel_error_fine_percent = (abs(f_extrap - f3) / abs(f_extrap)) * 100.0

    # Relative step change between medium and fine mesh
    e32 = abs(diff_32) / abs(f3)

    # Grid Convergence Index (GCI) for fine mesh (ASME V&V 20)
    gci_fine_percent = (safety_factor * e32 / (r**p - 1.0)) * 100.0

    return {
        "refinement_ratio": r,
        "apparent_order_p": p,
        "extrapolated_value": f_extrap,
        "fine_mesh_discretization_error_percent": rel_error_fine_percent,
        "grid_convergence_index_gci_percent": gci_fine_percent,
    }


if __name__ == "__main__":
    res = solve_mesh_convergence(40.0, 20.0, 10.0, 18.240, 19.680, 20.040)
    print("Mesh Convergence Reference Results:", res)
