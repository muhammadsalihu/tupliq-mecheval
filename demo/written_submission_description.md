# micro1 Eval Hackathon — Written Submission Description
## Project: MechEval (Mechanical Engineering AI Evaluation Benchmark)

### 1. What Was Built
MechEval is an open-source, deterministic, code-graded evaluation benchmark designed to assess whether frontier AI models can solve professional mechanical engineering problems without producing physically invalid solutions. 

The repository consists of:
- **5 High-Fidelity Engineering Tasks**: Cantilever beam bending under point and self-weight loading, stepped axial bar equilibrium with intermediate forces, statically indeterminate propped cantilever compatibility, constrained thermo-elastic expansion with a clearance gap, and finite element mesh convergence with stress singularity detection.
- **Independently Checked Ground Truths**: Reference solutions derived symbolically via SymPy and verified against classical elasticity theory and independent 1D Euler-Bernoulli direct stiffness finite element simulations.
- **Deterministic Automated Graders**: Configurable relative/absolute tolerance graders (1.0% threshold) tested and verified across 33 automated Pytest test cases.
- **Evaluation Harness & Reproducibility Suite**: Multi-trial runner recording full transcripts, token latency, cost, and generating summary tables and comparison charts.

---

### 2. Which Capability Is Evaluated
MechEval evaluates **physical constraint reasoning, kinematic compatibility enforcement, and mathematical rigor in continuum and structural mechanics**. Unlike general coding benchmarks (HumanEval, SWE-bench) that evaluate syntactic execution, MechEval evaluates whether an AI system respects fundamental conservation laws:
- Equilibrium of forces and moments ($\sum F = 0, \sum M = 0$).
- Superposition of dead weight and live equipment loads.
- Kinematic boundary conditions and deformation compatibility in indeterminate structures ($w(L) = 0$).
- Unilateral contact constraints preventing rigid boundary penetration.
- Asymptotic discretization error convergence vs mathematical stress singularities ($K_t \to \infty$).

---

### 3. Why the Capability Matters Professionally
In civil, aerospace, and mechanical engineering, an analytical error is not a software crash—it is a physical disaster. If an autonomous engineering assistant or copilot:
- Fails to include beam self-weight, structures can deflect beyond code limits or fail in bending under full load.
- Guesses symmetric 50/50 support reactions on an indeterminate beam, the fixed connection will be under-designed by 20%, risking joint shearing.
- Ignores clearance gaps during thermal expansion, cooling piping or turbine blades will experience unpredicted thermal stresses leading to low-cycle fatigue cracks.
- Fails to recognize a stress singularity, engineering teams can waste thousands of dollars attempting to converge an unfilleted sharp corner in FEA.

---

### 4. What Limitations Were Discovered
Our evaluation across 30 trials with frontier models (GPT-4o and Claude 3.5 Sonnet) revealed four critical limitations:
1. **The Consistency Collapse ($\text{pass@}3 = 80.0\%$ vs $\text{pass}^3 = 0.0\%$):** Models frequently solve a problem correctly on one attempt and fail on subsequent identical runs. Across all 5 tasks, neither model achieved 100% consistency ($\text{pass}^3 = 0.0\%$).
2. **Statical Indeterminacy Hallucination (0% Pass Rate):** Both models achieved a 0% pass rate on the propped cantilever task. They repeatedly ignored deformation compatibility, hallucinating symmetric 50/50 reaction forces ($R_A = R_B = 24$ kN instead of $30$ kN and $18$ kN).
3. **Boundary Condition Penetration:** In thermal expansion, models allowed an expanding metal bar to physically penetrate an immovable rigid stop, reporting actual elongation equal to unconstrained growth.
4. **Stress Singularity Blindness:** In finite element verification, models failed to identify that internal 90-degree sharp corners have infinite theoretical stress ($K_t \to \infty$) and cannot converge under mesh refinement.

---

### 5. What the Results Reveal About AI Engineering Performance
The results reveal a fundamental dichotomy: **frontier models excel at mechanical engineering jargon and textbook equation recall, but fail at holistic constraint satisfaction and multi-step boundary enforcement**. 

When tasks involve isolated single-step equations, models succeed. But when multiple physical phenomena interact—such as an intermediate force reversing the normal force diagram, or dead weight adding to a tip load, or a physical gap transitioning from free expansion to compressive stress—models fall back on generic heuristic templates. 

**Core Takeaway:** Today's frontier LLMs cannot be safely deployed for autonomous engineering calculations without deterministic, code-based verification harnesses like MechEval to check their outputs against governing physical laws.
