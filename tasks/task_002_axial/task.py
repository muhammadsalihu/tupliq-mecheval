"""
Task 002: Stepped Axial Bar Under Intermediate Loading
Evaluates the model's ability to apply the method of sections, calculate internal normal force
distribution, compute axial stresses across differing cross-sections, and determine cumulative elongation.
"""

from typing import Dict, Any, List
from tasks.base import BaseTask
from graders.simulation_grader import ParameterSpec
from reference.analytical.axial import solve_stepped_axial_bar


class SteppedAxialBarTask(BaseTask):
    task_id = "task_002_axial"
    title = "Stepped Axial Bar Under Intermediate Loading"
    category = "Solid Mechanics / Axial Deformation"
    description = (
        "Perform internal equilibrium, stress, elongation, and strain energy calculations "
        "for a two-segment circular stepped bar fixed at one end, subjected to an intermediate load "
        "and an end load."
    )
    units_convention = "SI Units (m, N, Pa/MPa, mm, J)"

    # Benchmark parameters
    length_1_m: float = 1.20
    diameter_1_m: float = 0.050        # d1 = 50 mm
    elastic_modulus_1_GPa: float = 70.0 # Aluminum E1 = 70 GPa

    length_2_m: float = 0.80
    diameter_2_m: float = 0.030        # d2 = 30 mm
    elastic_modulus_2_GPa: float = 200.0 # Steel E2 = 200 GPa

    intermediate_load_N: float = 45000.0  # F_int = 45 kN directed toward wall (-x)
    end_load_N: float = 80000.0           # F_end = 80 kN directed away from wall (+x)

    def get_input_parameters(self) -> Dict[str, Any]:
        return {
            "length_1_m": self.length_1_m,
            "diameter_1_m": self.diameter_1_m,
            "elastic_modulus_1_GPa": self.elastic_modulus_1_GPa,
            "length_2_m": self.length_2_m,
            "diameter_2_m": self.diameter_2_m,
            "elastic_modulus_2_GPa": self.elastic_modulus_2_GPa,
            "intermediate_load_N": self.intermediate_load_N,
            "end_load_N": self.end_load_N,
        }

    def get_reference_solution(self) -> Dict[str, Any]:
        return solve_stepped_axial_bar(
            length_1_m=self.length_1_m,
            diameter_1_m=self.diameter_1_m,
            elastic_modulus_1_GPa=self.elastic_modulus_1_GPa,
            length_2_m=self.length_2_m,
            diameter_2_m=self.diameter_2_m,
            elastic_modulus_2_GPa=self.elastic_modulus_2_GPa,
            intermediate_load_N=self.intermediate_load_N,
            end_load_N=self.end_load_N,
        )

    def get_grader_specs(self) -> List[ParameterSpec]:
        return [
            ParameterSpec(
                name="normal_force_seg1_N",
                description="Internal normal force N1 in Segment 1 in N (positive for tension)",
                unit="N",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="normal_force_seg2_N",
                description="Internal normal force N2 in Segment 2 in N (positive for tension)",
                unit="N",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="wall_reaction_N",
                description="Magnitude of horizontal reaction force at the fixed wall x=0 in N",
                unit="N",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="stress_seg1_MPa",
                description="Axial normal stress sigma1 in Segment 1 in MPa",
                unit="MPa",
                rel_tol=0.01,
                weight=1.2,
            ),
            ParameterSpec(
                name="stress_seg2_MPa",
                description="Axial normal stress sigma2 in Segment 2 in MPa",
                unit="MPa",
                rel_tol=0.01,
                weight=1.2,
            ),
            ParameterSpec(
                name="elongation_seg1_mm",
                description="Elongation delta1 of Segment 1 in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="elongation_seg2_mm",
                description="Elongation delta2 of Segment 2 in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="tip_deflection_mm",
                description="Total axial displacement at the free tip x = L1 + L2 in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="strain_energy_J",
                description="Total strain energy stored in the stepped bar in Joules",
                unit="J",
                rel_tol=0.01,
                weight=1.0,
            ),
        ]

    def get_prompt(self) -> str:
        return f"""You are acting as a professional mechanical engineer.
Analyze the following stepped cylindrical bar subjected to axial loading.

### Problem Geometry & Loading:
The bar is aligned horizontally along the x-axis, fixed rigidly to a wall at x = 0.
It consists of two segments:
- Segment 1 (from x = 0 to x = {self.length_1_m} m):
  - Length: L1 = {self.length_1_m} m
  - Diameter: d1 = {self.diameter_1_m} m (circular cross-section)
  - Material: Aluminum alloy with Elastic Modulus E1 = {self.elastic_modulus_1_GPa} GPa
- Intermediate Junction (at x = {self.length_1_m} m):
  - A concentrated axial load of F_int = {self.intermediate_load_N} N is applied directed toward the wall (negative x direction).
- Segment 2 (from x = {self.length_1_m} m to x = {self.length_1_m + self.length_2_m} m):
  - Length: L2 = {self.length_2_m} m
  - Diameter: d2 = {self.diameter_2_m} m (circular cross-section)
  - Material: Structural Steel with Elastic Modulus E2 = {self.elastic_modulus_2_GPa} GPa
- Free End (at x = {self.length_1_m + self.length_2_m} m):
  - A concentrated axial load of F_end = {self.end_load_N} N is applied directed away from the wall (positive x direction, tension).

### Required Deliverable:
Perform static equilibrium and axial deformation analysis.
You must return your numerical results strictly in a JSON code block formatted exactly as shown below:

```json
{{
  "normal_force_seg1_N": <float, internal normal force in segment 1 in N (positive for tension)>,
  "normal_force_seg2_N": <float, internal normal force in segment 2 in N (positive for tension)>,
  "wall_reaction_N": <float, magnitude of support reaction force at fixed wall in N>,
  "stress_seg1_MPa": <float, axial normal stress in segment 1 in MPa>,
  "stress_seg2_MPa": <float, axial normal stress in segment 2 in MPa>,
  "elongation_seg1_mm": <float, elongation of segment 1 in mm>,
  "elongation_seg2_mm": <float, elongation of segment 2 in mm>,
  "tip_deflection_mm": <float, total cumulative displacement at the free tip in mm>,
  "strain_energy_J": <float, total elastic strain energy in the system in Joules>
}}
```

Ensure all units match the requested schema. Do not include units or text inside the JSON values.
"""
