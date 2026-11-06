"""
Task 001: Cantilever Beam Analysis
Evaluates the model's ability to calculate beam section properties, internal reaction forces,
maximum bending stress, transverse shear stress, and tip deflection under combined point load and self-weight.
"""

from typing import Dict, Any, List
from tasks.base import BaseTask
from graders.simulation_grader import ParameterSpec
from reference.analytical.cantilever import solve_cantilever_analytical


class CantileverBeamTask(BaseTask):
    task_id = "task_001_cantilever"
    title = "Cantilever Beam Under Point Load and Distributed Self-Weight"
    category = "Structural Mechanics / Beam Theory"
    description = (
        "Calculate cross-sectional properties, reaction forces, root bending moment, "
        "maximum bending normal stress, maximum transverse shear stress, and tip deflection "
        "for a prismatic cantilever beam carrying a tip point load and its own self-weight."
    )
    units_convention = "SI Units (m, N, kg, Pa/MPa, mm)"

    # Fixed benchmark input parameters
    length_m: float = 2.50         # Beam span L = 2.5 meters
    width_m: float = 0.060         # Cross-section base b = 60 mm (0.060 m)
    height_m: float = 0.120        # Cross-section depth h = 120 mm (0.120 m)
    elastic_modulus_GPa: float = 210.0  # Structural Steel E = 210 GPa
    density_kg_m3: float = 7850.0       # Steel density rho = 7850 kg/m^3
    tip_load_N: float = 6500.0          # Vertical downward tip point load P = 6.5 kN
    gravity_m_s2: float = 9.81          # Standard gravity g = 9.81 m/s^2

    def get_input_parameters(self) -> Dict[str, Any]:
        return {
            "length_m": self.length_m,
            "width_m": self.width_m,
            "height_m": self.height_m,
            "elastic_modulus_GPa": self.elastic_modulus_GPa,
            "density_kg_m3": self.density_kg_m3,
            "tip_load_N": self.tip_load_N,
            "gravity_m_s2": self.gravity_m_s2,
        }

    def get_reference_solution(self) -> Dict[str, Any]:
        return solve_cantilever_analytical(
            length_m=self.length_m,
            width_m=self.width_m,
            height_m=self.height_m,
            elastic_modulus_GPa=self.elastic_modulus_GPa,
            density_kg_m3=self.density_kg_m3,
            tip_load_N=self.tip_load_N,
            gravity_m_s2=self.gravity_m_s2,
        )

    def get_grader_specs(self) -> List[ParameterSpec]:
        # 1.0% relative tolerance on all engineering parameters
        return [
            ParameterSpec(
                name="second_moment_of_area_m4",
                description="Second moment of area I about neutral axis (b*h^3/12)",
                unit="m^4",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="section_modulus_m3",
                description="Elastic section modulus Z about neutral axis (b*h^2/6)",
                unit="m^3",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="support_reaction_N",
                description="Vertical support reaction force at fixed root x=0 (P + w0*L)",
                unit="N",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="root_bending_moment_Nm",
                description="Magnitude of bending moment at fixed root x=0 (P*L + w0*L^2/2)",
                unit="N*m",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="max_bending_stress_MPa",
                description="Maximum bending normal stress in beam (at root outer fiber) in MPa",
                unit="MPa",
                rel_tol=0.01,
                weight=1.5,
            ),
            ParameterSpec(
                name="max_shear_stress_MPa",
                description="Maximum transverse shear stress (at neutral axis of root) in MPa",
                unit="MPa",
                rel_tol=0.01,
                weight=1.0,
            ),
            ParameterSpec(
                name="tip_deflection_mm",
                description="Total downward vertical deflection at the tip x=L in mm",
                unit="mm",
                rel_tol=0.01,
                weight=1.5,
            ),
        ]

    def get_prompt(self) -> str:
        return f"""You are acting as a professional mechanical/structural engineer.
Analyze the following prismatic cantilever beam under combined point loading and distributed self-weight.

### Beam Specifications:
- Span length: L = {self.length_m} m
- Cross-section: Rectangular, width b = {self.width_m} m (horizontal), depth h = {self.height_m} m (vertical)
- Material: Structural Steel
  - Elastic Modulus: E = {self.elastic_modulus_GPa} GPa
  - Density: rho = {self.density_kg_m3} kg/m^3
- Loading:
  - Downward point load at free tip (x = L): P = {self.tip_load_N} N
  - Self-weight distributed load along the span due to gravity: g = {self.gravity_m_s2} m/s^2 (w0 = rho * g * b * h)
- Boundary conditions:
  - Fully clamped/fixed at root x = 0 (zero displacement and zero slope)
  - Free at tip x = L

### Required Deliverable:
Compute the exact values using Euler-Bernoulli beam theory.
You must return your final numerical results strictly in a JSON code block formatted exactly as shown below:

```json
{{
  "second_moment_of_area_m4": <float, second moment of area I in m^4>,
  "section_modulus_m3": <float, elastic section modulus Z in m^3>,
  "support_reaction_N": <float, total vertical reaction force at fixed root in N>,
  "root_bending_moment_Nm": <float, magnitude of bending moment at fixed root in N*m>,
  "max_bending_stress_MPa": <float, maximum bending normal stress at the root in MPa>,
  "max_shear_stress_MPa": <float, maximum transverse shear stress at the root in MPa>,
  "tip_deflection_mm": <float, total downward deflection at the tip in mm>
}}
```

Ensure all units match the requested schema (e.g. stresses in MPa, deflection in mm, moments in N*m, area moments in m^4).
Do not include units inside the JSON values; provide pure numeric floating-point values.
"""
