"""
Task 004: Constrained Thermal Expansion With Pre-existing Gap
Evaluates the model's ability to analyze thermo-elastic behavior under kinematic contact constraints,
distinguish free vs restrained expansion, identify contact onset, and calculate resulting thermal stress and reactions.
"""

from typing import Dict, Any, List
from tasks.base import BaseTask
from graders.simulation_grader import ParameterSpec
from reference.analytical.thermal import solve_thermal_expansion_gap


class ThermalExpansionGapTask(BaseTask):
    task_id = "task_004_thermal"
    title = "Constrained Thermal Expansion of a Bar with Initial Clearance Gap"
    category = "Thermal / Thermo-Elasticity"
    description = (
        "Analyze a prismatic metal bar fixed at one end with an initial clearance gap to a rigid stop at the other. "
        "Calculate unconstrained free expansion, critical temperature to close the gap, actual bar elongation, "
        "restrained displacement, resulting compressive thermal stress, and support reaction force."
    )
    units_convention = "SI Units (m, mm, deg C, Pa/MPa, N)"

    # Benchmark parameters
    length_m: float = 1.50
    width_m: float = 0.040                 # 40 mm square cross-section
    height_m: float = 0.040                # 40 mm square cross-section
    elastic_modulus_GPa: float = 193.0     # Stainless Steel 304 E = 193 GPa
    thermal_expansion_coeff: float = 17.3e-6 # alpha = 17.3 x 10^-6 / deg C
    initial_temp_C: float = 20.0           # T0 = 20 deg C
    final_temp_C: float = 110.0            # T_final = 110 deg C (delta T = 90 deg C)
    clearance_gap_m: float = 0.00120       # Gap delta_0 = 1.20 mm

    def get_input_parameters(self) -> Dict[str, Any]:
        return {
            "length_m": self.length_m,
            "width_m": self.width_m,
            "height_m": self.height_m,
            "elastic_modulus_GPa": self.elastic_modulus_GPa,
            "thermal_expansion_coeff": self.thermal_expansion_coeff,
            "initial_temp_C": self.initial_temp_C,
            "final_temp_C": self.final_temp_C,
            "clearance_gap_m": self.clearance_gap_m,
        }

    def get_reference_solution(self) -> Dict[str, Any]:
        return solve_thermal_expansion_gap(
            length_m=self.length_m,
            width_m=self.width_m,
            height_m=self.height_m,
            elastic_modulus_GPa=self.elastic_modulus_GPa,
            thermal_expansion_coeff=self.thermal_expansion_coeff,
            initial_temp_C=self.initial_temp_C,
            final_temp_C=self.final_temp_C,
            clearance_gap_m=self.clearance_gap_m,
        )

    def get_grader_specs(self) -> List[ParameterSpec]:
        return [
            ParameterSpec(
                name="free_thermal_expansion_mm",
                description="Hypothetical free thermal elongation without the rigid stop in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="temperature_to_close_gap_C",
                description="Absolute temperature at which the bar first makes contact with the stop in deg C",
                unit="deg C",
                rel_tol=0.01,
                weight=1.2,
            ),
            ParameterSpec(
                name="actual_elongation_mm",
                description="Actual physical elongation of the bar at final temperature in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="restrained_expansion_mm",
                description="Amount of thermal expansion prevented by the rigid stop in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="thermal_stress_MPa",
                description="Magnitude of compressive thermal normal stress induced at final temperature in MPa",
                unit="MPa",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="reaction_force_N",
                description="Magnitude of reaction force exerted by the rigid stop on the bar in N",
                unit="N",
                rel_tol=0.01,
                weight=1.2,
            ),
        ]

    def get_prompt(self) -> str:
        return f"""You are acting as a professional mechanical engineer.
Analyze the thermo-elastic response of the following constrained bar with an initial gap.

### Geometry, Material & Operating Conditions:
- The bar has length L = {self.length_m} m.
- Cross-section is square: width b = {self.width_m} m, height h = {self.height_m} m.
- Material: Stainless Steel 304
  - Elastic Modulus: E = {self.elastic_modulus_GPa} GPa
  - Linear Coefficient of Thermal Expansion: alpha = {self.thermal_expansion_coeff:.1e} 1/°C
- Boundary Conditions:
  - At x = 0: Clamped rigidly to an immovable wall.
  - At x = L: There is an initial clearance gap of delta_0 = {self.clearance_gap_m * 1000.0} mm between the end of the bar and an immovable rigid stop.
- Temperature Conditions:
  - Initial stress-free temperature: T0 = {self.initial_temp_C} °C
  - Final uniform operating temperature: T_final = {self.final_temp_C} °C

### Required Deliverable:
Evaluate whether the thermal expansion closes the gap and determine the mechanical state of the bar.
Return your results strictly in a JSON code block formatted exactly as shown below:

```json
{{
  "free_thermal_expansion_mm": <float, hypothetical unconstrained thermal expansion in mm>,
  "temperature_to_close_gap_C": <float, temperature T in °C at which the gap is exactly closed>,
  "actual_elongation_mm": <float, actual physical elongation of the bar in mm at T_final>,
  "restrained_expansion_mm": <float, elongation restrained by the rigid stop in mm>,
  "thermal_stress_MPa": <float, magnitude of compressive thermal stress at T_final in MPa>,
  "reaction_force_N": <float, magnitude of contact reaction force at the rigid stop in N>
}}
```

Ensure all units match the requested schema. Provide pure floating point values.
"""
