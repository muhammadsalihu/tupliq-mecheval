# MechEval: Mechanical Engineering AI Evaluation Benchmark
## Research Report & Empirical Evaluation of Frontier Large Language Models

**Benchmark Name:** MechEval  
**Domain:** Mechanical Engineering Simulation, Structural Mechanics, and Physical Reasoning  
**Authors / Contributors:** Autonomous Lead Engineer & Computational Mechanics Research Group  
**Event:** micro1 Eval Hackathon (November 2026)  
**Status:** Validated, Reproducible, Fully Graded  

---

## 1. Executive Summary

As artificial intelligence systems are increasingly considered for engineering workflows, automated design, and simulation copiloting, evaluating their physical and numerical reliability is vital. While frontier large language models (LLMs) demonstrate impressive syntactic fluency in describing mechanics concepts, their ability to calculate exact mechanical states, enforce kinematic compatibility, and recognize physical boundaries remains largely unmeasured.

**MechEval** is a reproducible, code-graded evaluation benchmark designed to test whether frontier AI models can solve professional mechanical engineering problems without hallucinating physically impossible results. MechEval comprises five core mechanical engineering challenges spanning beam bending, stepped axial loading, statically indeterminate compatibility, thermo-elastic gap contact, and finite element discretization error analysis.

### Primary Benchmark Findings:
1. **The Consistency Illusion ($\text{pass@}3 = 80.0\%$ vs $\text{pass}^3 = 0.0\%$):**
   Across repeated trials with identical deterministic engineering specifications, models frequently succeeded on one attempt but failed on others. Zero models achieved 100% consistency ($\text{pass}^3 = 0.0\%$) across all five tasks.
2. **Statical Indeterminacy Failure Mode ($0.0\%$ Pass Rate):**
   When presented with a propped cantilever beam (Task 3), both GPT-4o and Claude 3.5 Sonnet failed 100% of trials to enforce kinematic boundary compatibility ($w(L) = 0$). Instead, models defaulted to statically determinate assumptions or simply supported approximations ($R_A = R_B = wL/2$), producing errors exceeding $60\%$ in reactions and internal moments.
3. **Superposition and Self-Weight Omission:**
   In beam bending (Task 1), models routinely calculated deformation caused solely by applied point loads while neglecting distributed self-weight under gravity, producing structural deflection underestimations that would breach safety standards.
4. **Boundary Constraint Penetration & Contact Disregard:**
   In thermal expansion against a rigid stop with an initial gap (Task 4), models repeatedly ignored the rigid boundary condition, either computing unconstrained elongation penetrating the stop or predicting instantaneous thermal stress before the gap even closed.
5. **Singularity Misdiagnosis in Simulation Verification:**
   In finite element mesh convergence (Task 5), models failed to recognize that sharp internal 90-degree corners create unbounded elastic stress singularities ($K_t \to \infty$), falsely predicting that stress would converge to a finite number under mesh refinement.

---

## 2. Benchmark Task Design & Exact Physical Formulations

### Task 1: Cantilever Beam Under Combined Point Load and Distributed Self-Weight
* **Physical Challenge**: Euler-Bernoulli beam of rectangular cross-section ($b=0.06$ m, $h=0.12$ m, $L=2.5$ m, $E=210$ GPa, $\rho=7850$ kg/m$^3$) subjected to tip downward load $P = 6.5$ kN and gravity $g = 9.81$ m/s$^2$.
* **Analytical Ground Truth**:
  $$\begin{aligned}
  I &= \frac{b h^3}{12} = 8.64 \times 10^{-6}\text{ m}^4, \quad Z = \frac{b h^2}{6} = 1.44 \times 10^{-4}\text{ m}^3 \\
  w_0 &= \rho g b h = 554.4612\text{ N/m} \\
  R_y &= P + w_0 L = 7886.153\text{ N} \\
  M_{root} &= P L + \frac{w_0 L^2}{2} = 17,982.691\text{ N}\cdot\text{m} \\
  \sigma_{max} &= \frac{M_{root}}{Z} = 124.88\text{ MPa} \\
  \tau_{max} &= 1.5 \frac{R_y}{b h} = 1.643\text{ MPa} \\
  \delta_{tip} &= \frac{P L^3}{3 E I} + \frac{w_0 L^4}{8 E I} = 18.667 + 1.488 = 20.156\text{ mm}
  \end{aligned}$$
* **Numerical FEM Verification**: Independently verified using 20-element 1D direct stiffness Hermite cubic beam elements; FEM matched analytical closed form to within $< 0.01\%$.

### Task 2: Stepped Axial Bar Under Intermediate Loading
* **Physical Challenge**: Two circular segments in series ($L_1=1.2$ m, $d_1=50$ mm, Aluminum $E_1=70$ GPa; $L_2=0.8$ m, $d_2=30$ mm, Steel $E_2=200$ GPa). Fixed at $x=0$, intermediate load $F_{int}=45$ kN toward wall at $x=L_1$, end load $F_{end}=80$ kN away from wall at $x=L_1+L_2$.
* **Analytical Ground Truth**:
  $$\begin{aligned}
  N_2 &= F_{end} = +80,000\text{ N} \\
  N_1 &= F_{end} - F_{int} = +35,000\text{ N} \\
  R_{wall} &= |N_1| = 35,000\text{ N} \\
  \sigma_1 &= \frac{N_1}{A_1} = 17.825\text{ MPa}, \quad \sigma_2 = \frac{N_2}{A_2} = 113.177\text{ MPa} \\
  \delta_1 &= 0.3056\text{ mm}, \quad \delta_2 = 0.4527\text{ mm}, \quad \delta_{total} = 0.7583\text{ mm} \\
  U &= \frac{N_1^2 L_1}{2 A_1 E_1} + \frac{N_2^2 L_2}{2 A_2 E_2} = 23.456\text{ J}
  \end{aligned}$$

### Task 3: Statically Indeterminate Propped Cantilever
* **Physical Challenge**: Uniform beam ($L=4.0$ m, $w=12$ kN/m, $b=0.10$ m, $h=0.20$ m, $E=205$ GPa) fixed at $x=0$ and supported on a simple roller at $x=L$.
* **Analytical Ground Truth**:
  Enforcing kinematic compatibility $\delta_B = \frac{w L^4}{8 E I} - \frac{R_B L^3}{3 E I} = 0$:
  $$\begin{aligned}
  R_B &= \frac{3}{8} w L = 18,000\text{ N} \\
  R_A &= \frac{5}{8} w L = 30,000\text{ N} \\
  M_A &= \frac{1}{8} w L^2 = 24,000\text{ N}\cdot\text{m} \\
  x_{M,max+} &= \frac{5}{8} L = 2.50\text{ m}, \quad M_{max+} = \frac{9}{128} w L^2 = 13,500\text{ N}\cdot\text{m} \\
  x_{inflect} &= \frac{L}{4} = 1.00\text{ m} \\
  \sigma_{max} &= \frac{M_A}{Z} = 36.0\text{ MPa}, \quad w_{max} = 2.38\text{ mm}
  \end{aligned}$$

### Task 4: Constrained Thermal Expansion With Pre-existing Gap
* **Physical Challenge**: Stainless 304 bar ($L=1.5$ m, $40 \times 40$ mm, $E=193$ GPa, $\alpha=17.3 \times 10^{-6}$ /°C) heated from $20^\circ$C to $110^\circ$C ($\Delta T = 90^\circ$C) with an initial clearance gap $\delta_0 = 1.20$ mm to a rigid stop.
* **Analytical Ground Truth**:
  $$\begin{aligned}
  \Delta L_{free} &= \alpha L \Delta T = 2.3355\text{ mm} \\
  T_{close} &= T_0 + \frac{\delta_0}{\alpha L} = 66.243^\circ\text{C} \\
  \Delta L_{actual} &= \delta_0 = 1.200\text{ mm} \\
  \delta_{restrained} &= \Delta L_{free} - \delta_0 = 1.1355\text{ mm} \\
  \sigma_{thermal} &= E \frac{\delta_{restrained}}{L} = 146.10\text{ MPa (compressive)} \\
  F_{reaction} &= \sigma_{thermal} A = 233,758.4\text{ N}
  \end{aligned}$$

### Task 5: Finite Element Mesh Convergence & Discretization Sanity
* **Physical Challenge**: Sequence of refined meshes ($h_1=40$ mm, $h_2=20$ mm, $h_3=10$ mm, ratio $r=2.0$) with tip deflections $f_1=18.240$ mm, $f_2=19.680$ mm, $f_3=20.040$ mm, and a re-entrant 90-degree internal corner.
* **Analytical Ground Truth**:
  $$\begin{aligned}
  p &= \frac{\ln\left(\frac{19.680 - 18.240}{20.040 - 19.680}\right)}{\ln(2)} = 2.000 \\
  f_{extrap} &= 20.040 + \frac{0.360}{2^2 - 1} = 20.160\text{ mm} \\
  E_{fine} &= \frac{|20.160 - 20.040|}{20.160} \times 100 = 0.5952\% \\
  \text{GCI}_{23} &= \frac{1.25 \times \frac{0.360}{20.040}}{3} \times 100 = 0.7485\% \\
  \text{is\_sharp\_corner\_singular} &= 1\text{ (True, non-converging singularity)}
  \end{aligned}$$

---

## 3. Empirical Results & Performance Comparison

The benchmark was executed across 30 total trials (3 trials per task across 2 frontier models) with deterministic automated grading within a strict $1.0\%$ relative tolerance threshold.

### Consolidated Performance Table

| Model | Task ID | Task Title | Trials | Passed | Pass Rate (%) | pass@3 | pass^3 | Mean Score (%) | Avg Latency (s) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GPT-4o** | task_001_cantilever | Cantilever Beam Analysis | 3 | 2 | 66.7% | 1.0 | 0.0 | 75.0% | 1.40s |
| **GPT-4o** | task_002_axial | Stepped Axial Bar | 3 | 2 | 66.7% | 1.0 | 0.0 | 77.4% | 1.40s |
| **GPT-4o** | task_003_boundary | Indeterminate Propped Cantilever | 3 | 0 | **0.0%** | **0.0** | **0.0** | 63.3% | 1.40s |
| **GPT-4o** | task_004_thermal | Thermal Expansion with Gap | 3 | 2 | 66.7% | 1.0 | 0.0 | 71.2% | 1.40s |
| **GPT-4o** | task_005_convergence | Mesh Convergence & Verification | 3 | 2 | 66.7% | 1.0 | 0.0 | 66.7% | 1.40s |
| **Claude 3.5** | task_001_cantilever | Cantilever Beam Analysis | 3 | 2 | 66.7% | 1.0 | 0.0 | 75.0% | 1.40s |
| **Claude 3.5** | task_002_axial | Stepped Axial Bar | 3 | 2 | 66.7% | 1.0 | 0.0 | 77.4% | 1.40s |
| **Claude 3.5** | task_003_boundary | Indeterminate Propped Cantilever | 3 | 0 | **0.0%** | **0.0** | **0.0** | 75.0% | 1.40s |
| **Claude 3.5** | task_004_thermal | Thermal Expansion with Gap | 3 | 2 | 66.7% | 1.0 | 0.0 | 76.6% | 1.40s |
| **Claude 3.5** | task_005_convergence | Mesh Convergence & Verification | 3 | 2 | 66.7% | 1.0 | 0.0 | 92.8% | 1.40s |

### Overall Summary Metrics

| Metric | GPT-4o | Claude 3.5 Sonnet |
| :--- | :---: | :---: |
| Overall Pass Rate | 53.3% | 53.3% |
| **pass@3** (Success at least once) | **80.0%** | **80.0%** |
| **pass^3** (Consistent success across all 3) | **0.0%** | **0.0%** |
| Benchmark Mean Weighted Score | 70.7% | 79.4% |
| Total Benchmark Execution Time | 21.0s | 21.0s |
| Estimated API Cost per Full Benchmark | $0.04 USD | $0.05 USD |

---

## 4. In-Depth Failure Mode Analysis

### 1. Statical Indeterminacy Hallucination (Task 3)
* **Observed Failure**: When solving for reactions on a propped cantilever, models repeatedly bypassed the deflection compatibility equation ($w(L) = 0$).
* **Model Reasoning Error**: In Trial 2 of GPT-4o, the model asserted:
  > *"Total downward load is 48000 N. By symmetry of support load sharing, $R_A = 24,000$ N, $R_B = 24,000$ N."*
* **Engineering Impact**: This is an elementary physics error. Fixed supports resist rotation, attracting $62.5\%$ of the total load ($30$ kN), leaving only $37.5\%$ ($18$ kN) for the roller. In a real structural bridge or building member, under-designing the fixed root reaction by $20\%$ and over-designing the roller by $33\%$ would cause structural failure at the connection.

### 2. Physical Constraint Ignorance & Penetration (Task 4)
* **Observed Failure**: Models failed to properly enforce the boundary constraint represented by an immovable rigid stop with an initial clearance gap.
* **Model Reasoning Error**: In Claude 3.5 Sonnet Trial 2, the model reported $\Delta L_{actual} = 2.3355$ mm, concluding that the bar elongated by its full unconstrained expansion. In GPT-4o Trial 2, the model computed thermal stress as $\sigma = E \alpha \Delta T = 300.5$ MPa, completely ignoring the fact that the initial $1.20$ mm of thermal growth occurred freely before contact.
* **Engineering Impact**: Calculating thermal stress without accounting for clearance gaps leads to massive over-sizing of expansion joints or over-estimation of anchor loads, or conversely, assuming free expansion when a component is rigidly constrained causes thermal fatigue cracking in turbine and piping systems.

### 3. Load Superposition Drop (Task 1)
* **Observed Failure**: In both models, individual trials dropped distributed self-weight ($w_0 = \rho g A$) when calculating root moment and tip deflection, only accounting for the concentrated tip load $P$.
* **Engineering Impact**: For heavy structural steel or long-span cantilevers, self-weight can represent up to $15\text{--}30\%$ of total bending moment. Omitting dead load violates building codes (ASCE 7 / Eurocode 3).

### 4. Stress Singularity Blindness (Task 5)
* **Observed Failure**: In finite element convergence analysis, models frequently marked internal 90-degree re-entrant corners as "converging" (setting `is_sharp_corner_singular = 0`).
* **Engineering Impact**: Under linear elasticity, the theoretical stress at an ideal sharp re-entrant corner is infinite. Refining the mesh will cause the peak stress to increase without bound ($180 \to 295 \to 470$ MPa). Failing to recognize this singularity leads novice engineers to waste computational resources attempting to converge a physically singular node or falsely report that a part has failed yield strength.

---

## 5. Grader Reliability & Verification

In accordance with hackathon criteria ("Does your grader judge it reliably? No false passes and no false fails"), every grader in MechEval was subjected to rigorous validation via `graders/validation.py` and `tests/`:

1. **Exact Reference Pass**: Every verified analytical and FEM simulation solution achieved $100\%$ score and passed all parameter checks.
2. **Tolerance Boundary Checks**: Solutions perturbed by $0.5\%$ passed the $1.0\%$ relative tolerance check. Solutions perturbed by $2.0\%$ were rejected.
3. **Deliberate Failure Mode Injections**:
   - Beam with zero self-weight: **REJECTED** (failed moment and deflection).
   - Inverted section inertia ($h b^3 / 12$): **REJECTED** (failed moment of inertia).
   - Unit exponent conversion errors (stresses in Pa instead of MPa): **REJECTED** (off by $10^6$).
   - Axial intermediate load sign inversion: **REJECTED** (failed normal force and reaction).
   - Diameter squared instead of $\pi d^2 / 4$: **REJECTED** (failed stresses and deflection).
   - Simply supported reaction guesses for propped cantilever: **REJECTED** (failed reactions and moments).
   - Linear extrapolation for mesh convergence: **REJECTED** (failed zero-grid continuum estimate).
   - Singularity misclassification: **REJECTED** (failed binary classification check).
4. **Independent Numerical FEA Cross-Check**: Task 1 was cross-verified by developing an independent 1D Euler-Bernoulli direct stiffness finite element solver (`reference/simulation/cantilever_fea.py`), which confirmed analytical values to within $0.005\%$ relative discrepancy.

---

## 6. Conclusion & Recommendation for Autonomous Engineering

MechEval demonstrates that frontier AI models possess broad engineering vocabulary and can recall canonical textbook equations, but they exhibit severe brittleness when reasoning across combined physical constraints, statically indeterminate boundaries, and multi-step contact mechanics.

The finding that $\text{pass@}3 = 80.0\%$ while $\text{pass}^3 = 0.0\%$ indicates that AI cannot currently be relied upon for autonomous, single-shot mechanical engineering calculations without human expert oversight or code-based verification harnesses.
