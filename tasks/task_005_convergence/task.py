"""
Task 005: Mesh Convergence and Discretization Sanity Analysis
Evaluates the model's ability to assess finite element mesh convergence, calculate apparent order of convergence,
perform Richardson extrapolation to estimate continuum zero-grid error, compute the Grid Convergence Index (GCI),
and diagnose mathematical stress singularities.
"""

from typing import Dict, Any, List
from tasks.base import BaseTask
from graders.simulation_grader import ParameterSpec
from reference.analytical.convergence import solve_mesh_convergence


class MeshConvergenceTask(BaseTask):
    task_id = "task_005_convergence"
    title = "Finite Element Mesh Convergence and Discretization Error Analysis"
    category = "Computational Mechanics / Verification & Validation"
    description = (
        "Evaluate numerical simulation results across a 3-level mesh refinement hierarchy. "
        "Calculate the apparent order of convergence p, Richardson extrapolated continuum solution, "
        "fine-mesh relative discretization error, and Grid Convergence Index (GCI) per ASME V&V 20. "
        "Diagnose whether an internal re-entrant sharp corner represents a physical convergence or mathematical singularity."
    )
    units_convention = "Dimensionless ratios, mm, %"

    # Benchmark parameters
    h1_mm: float = 40.0   # Coarse mesh characteristic element size
    h2_mm: float = 20.0   # Medium mesh
    h3_mm: float = 10.0   # Fine mesh (uniform refinement ratio r = 2.0)

    f1_val: float = 18.240  # Coarse mesh displacement result (mm)
    f2_val: float = 19.680  # Medium mesh displacement result (mm)
    f3_val: float = 20.040  # Fine mesh displacement result (mm)
    safety_factor: float = 1.25  # Standard ASME V&V 20 safety factor

    # Re-entrant sharp 90-degree corner stress sequence across the meshes:
    # Mesh 1: 180.0 MPa, Mesh 2: 295.0 MPa, Mesh 3: 470.0 MPa
    is_sharp_corner_singular: int = 1  # 1 = True (mathematical singularity), 0 = False

    def get_input_parameters(self) -> Dict[str, Any]:
        return {
            "h1_mm": self.h1_mm,
            "h2_mm": self.h2_mm,
            "h3_mm": self.h3_mm,
            "f1_val": self.f1_val,
            "f2_val": self.f2_val,
            "f3_val": self.f3_val,
            "safety_factor": self.safety_factor,
        }

    def get_reference_solution(self) -> Dict[str, Any]:
        ref = solve_mesh_convergence(
            h1_mm=self.h1_mm,
            h2_mm=self.h2_mm,
            h3_mm=self.h3_mm,
            f1=self.f1_val,
            f2=self.f2_val,
            f3=self.f3_val,
            safety_factor=self.safety_factor,
        )
        ref["is_sharp_corner_singular"] = float(self.is_sharp_corner_singular)
        return ref

    def get_grader_specs(self) -> List[ParameterSpec]:
        return [
            ParameterSpec(
                name="apparent_order_p",
                description="Apparent order of convergence p calculated from mesh refinement data",
                unit="dimensionless",
                rel_tol=0.02,
                weight=1.5,
            ),
            ParameterSpec(
                name="extrapolated_value",
                description="Richardson-extrapolated continuum value (h -> 0) in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="fine_mesh_discretization_error_percent",
                description="Estimated relative discretization error of the fine mesh compared to extrapolated continuum value in %",
                unit="%",
                rel_tol=0.03,
                weight=1.2,
            ),
            ParameterSpec(
                name="grid_convergence_index_gci_percent",
                description="Grid Convergence Index (GCI) for the fine mesh with Fs = 1.25 in %",
                unit="%",
                rel_tol=0.03,
                weight=1.2,
            ),
            ParameterSpec(
                name="is_sharp_corner_singular",
                description="Classification of re-entrant sharp corner: 1 if mathematical singularity, 0 if physically converging",
                unit="binary (0 or 1)",
                rel_tol=0.001,
                abs_tol=0.001,
                weight=1.5,
            ),
        ]

    def get_prompt(self) -> str:
        return f"""You are acting as a computational mechanics & simulation verification engineer.
Perform a mesh convergence and discretization error verification study in accordance with ASME V&V 20 standards.

### Simulation Data:
A finite element model was solved across three systematically refined grid levels with a constant refinement ratio r = 2.0:
- Mesh 1 (Coarse, h1 = {self.h1_mm} mm): Tip displacement f1 = {self.f1_val} mm
- Mesh 2 (Medium, h2 = {self.h2_mm} mm): Tip displacement f2 = {self.f2_val} mm
- Mesh 3 (Fine,   h3 = {self.h3_mm} mm): Tip displacement f3 = {self.f3_val} mm

Additionally, a local stress study at an internal 90-degree sharp re-entrant re-entrant corner (notch radius r = 0 mm) yielded the following peak Von Mises stresses:
- Mesh 1 (h = {self.h1_mm} mm): 180.0 MPa
- Mesh 2 (h = {self.h2_mm} mm): 295.0 MPa
- Mesh 3 (h = {self.h3_mm} mm): 470.0 MPa

### Required Deliverable:
1. Compute the apparent order of convergence `p` using the three grid solutions.
2. Calculate the Richardson extrapolated continuum value as grid spacing h -> 0 (`extrapolated_value`).
3. Compute the relative discretization error percentage on the fine mesh (`fine_mesh_discretization_error_percent`).
4. Calculate the Grid Convergence Index for the fine mesh (`grid_convergence_index_gci_percent`) using ASME safety factor F_s = {self.safety_factor}.
5. Determine whether the stress at the re-entrant sharp corner is a non-converging mathematical stress singularity (`is_sharp_corner_singular`: 1 for Yes, 0 for No).

Return your numerical results strictly in a JSON code block formatted exactly as shown below:

```json
{{
  "apparent_order_p": <float, apparent order of convergence p>,
  "extrapolated_value": <float, Richardson extrapolated zero-grid displacement in mm>,
  "fine_mesh_discretization_error_percent": <float, fine mesh relative error in percent %>,
  "grid_convergence_index_gci_percent": <float, fine mesh GCI in percent %>,
  "is_sharp_corner_singular": <float or int, 1 if the sharp corner is an unbounded singularity, 0 if it physically converges>
}}
```

Provide pure numerical floating point values only.
"""
