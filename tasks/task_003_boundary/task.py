"""
Task 003: Boundary Conditions and Statically Indeterminate Beam Analysis
Evaluates the model's ability to recognize kinematic boundary constraints, enforce deflection
compatibility, compute indeterminate reaction forces/moments, and determine inflection points.
"""

from typing import Dict, Any, List
from tasks.base import BaseTask
from graders.simulation_grader import ParameterSpec
from reference.analytical.boundary import solve_propped_cantilever_analytical


class ProppedCantileverTask(BaseTask):
    task_id = "task_003_boundary"
    title = "Statically Indeterminate Propped Cantilever Under Uniform Load"
    category = "Structural Mechanics / Indeterminate Structures"
    description = (
        "Solve a statically indeterminate propped cantilever beam (fixed at x=0, simple roller support at x=L) "
        "under a uniform downward load. Calculate support reactions, clamping moment, contraflexure point, "
        "maximum positive moment location/magnitude, peak bending stress, and maximum deflection."
    )
    units_convention = "SI Units (m, N, N*m, MPa, mm)"

    # Benchmark parameters
    length_m: float = 4.00               # Span L = 4.0 m
    distributed_load_N_m: float = 12000.0 # w = 12 kN/m
    width_m: float = 0.100               # b = 100 mm (0.10 m)
    height_m: float = 0.200              # h = 200 mm (0.20 m)
    elastic_modulus_GPa: float = 205.0   # Structural Steel E = 205 GPa

    def get_input_parameters(self) -> Dict[str, Any]:
        return {
            "length_m": self.length_m,
            "distributed_load_N_m": self.distributed_load_N_m,
            "width_m": self.width_m,
            "height_m": self.height_m,
            "elastic_modulus_GPa": self.elastic_modulus_GPa,
        }

    def get_reference_solution(self) -> Dict[str, Any]:
        return solve_propped_cantilever_analytical(
            length_m=self.length_m,
            distributed_load_N_m=self.distributed_load_N_m,
            width_m=self.width_m,
            height_m=self.height_m,
            elastic_modulus_GPa=self.elastic_modulus_GPa,
        )

    def get_grader_specs(self) -> List[ParameterSpec]:
        return [
            ParameterSpec(
                name="roller_reaction_N",
                description="Vertical reaction force at roller support B (x = L) in N",
                unit="N",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="wall_vertical_reaction_N",
                description="Vertical reaction force at fixed wall A (x = 0) in N",
                unit="N",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="wall_moment_Nm",
                description="Magnitude of clamping moment at fixed wall A (x = 0) in N*m",
                unit="N*m",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="x_max_positive_moment_m",
                description="Location along the beam x from wall where positive bending moment is maximum in m",
                unit="m",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="max_positive_moment_Nm",
                description="Magnitude of maximum positive (sagging) bending moment in N*m",
                unit="N*m",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="x_contraflexure_m",
                description="Point of contraflexure (inflection point where M(x) = 0 between 0 and L) in m",
                unit="m",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="max_bending_stress_MPa",
                description="Maximum bending stress anywhere in the beam in MPa",
                unit="MPa",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="max_deflection_mm",
                description="Maximum downward vertical deflection of the beam in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.0,
            ),
        ]

    def get_prompt(self) -> str:
        return f"""You are acting as a professional structural engineer.
Analyze the following statically indeterminate beam structure.

### Beam Geometry, Boundary Conditions & Loading:
- Span length: L = {self.length_m} m
- Cross-section: Rectangular, width b = {self.width_m} m, height h = {self.height_m} m
- Material: Structural Steel with Elastic Modulus E = {self.elastic_modulus_GPa} GPa
- Support Conditions:
  - At x = 0 (Left End A): Fully clamped/fixed support (zero deflection, zero slope).
  - At x = L = {self.length_m} m (Right End B): Ideal roller/simple support (prevents vertical displacement, allows rotation).
- Loading:
  - A uniformly distributed downward load of w = {self.distributed_load_N_m} N/m applied across the full span [0, L].

### Required Deliverable:
Enforce kinematic compatibility and static equilibrium to solve for the indeterminate reactions and internal bending moments.
Return your results strictly in a JSON code block formatted exactly as shown below:

```json
{{
  "roller_reaction_N": <float, vertical reaction force at roller support B in N>,
  "wall_vertical_reaction_N": <float, vertical reaction force at fixed wall A in N>,
  "wall_moment_Nm": <float, magnitude of clamping moment at wall A in N*m>,
  "x_max_positive_moment_m": <float, coordinate x where positive bending moment is maximum in m>,
  "max_positive_moment_Nm": <float, maximum positive bending moment in N*m>,
  "x_contraflexure_m": <float, coordinate x of point of contraflexure (where M(x) = 0) between 0 and L in m>,
  "max_bending_stress_MPa": <float, absolute maximum bending stress anywhere in the beam in MPa>,
  "max_deflection_mm": <float, maximum downward deflection along the beam in mm>
}}
```

Ensure all units match the requested schema. Pure floating point numbers only.
"""
