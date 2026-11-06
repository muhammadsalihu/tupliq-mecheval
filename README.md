# MechEval: Mechanical Engineering AI Evaluation Benchmark

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 33 Passed](https://img.shields.io/badge/Tests-33%20Passed-brightgreen.svg)](tests/)
[![Eval: micro1 Hackathon](https://img.shields.io/badge/micro1-Eval%20Hackathon%202026-orange.svg)]()

> **MechEval** is a reproducible, code-graded AI evaluation benchmark that rigorously exposes physical reasoning limitations in frontier AI models performing professional mechanical and structural engineering tasks.

---

## Table of Contents
1. [Overview & Motivation](#1-overview--motivation)
2. [Target Audience & Engineering Importance](#2-target-audience--engineering-importance)
3. [Core Engineering Hypotheses & Failure Modes](#3-core-engineering-hypotheses--failure-modes)
4. [Benchmark Tasks Overview](#4-benchmark-tasks-overview)
5. [Task Inputs and Output Schemas](#5-task-inputs-and-output-schemas)
6. [Reference Solution Methodology](#6-reference-solution-methodology)
7. [Grading Logic & Rigorous Validation](#7-grading-logic--rigorous-validation)
8. [Installation & Setup](#8-installation--setup)
9. [Exact Commands to Run Benchmark](#9-exact-commands-to-run-benchmark)
10. [Models & Configurations Tested](#10-models--configurations-tested)
11. [Empirical Results Summary](#11-empirical-results-summary)
12. [In-Depth Performance Analysis](#12-in-depth-performance-analysis)
13. [Runtime and Inference Cost](#13-runtime-and-inference-cost)
14. [Known Limitations](#14-known-limitations)
15. [Data Sources & Licensing](#15-data-sources--licensing)
16. [AI-Assisted Development & Human Verification Disclosure](#16-ai-assisted-development--human-verification-disclosure)

---

## 1. Overview & Motivation
Frontier AI models (GPT-4o, Claude 3.5 Sonnet, etc.) can rapidly generate plausible-looking engineering derivations. However, in safety-critical physical systems (civil infrastructure, aerospace airframes, high-pressure piping, and machinery), a calculation that looks convincing but is physically invalid can cause structural collapse and catastrophic failure.

**MechEval** tests whether AI models can solve genuine, practical mechanical engineering problems involving:
- Superposition of multiple loads and self-weight dead load.
- Internal normal force diagrams using the method of sections.
- Statically indeterminate kinematic compatibility equations.
- Piecewise contact mechanics and constrained thermo-elastic expansion.
- Discretization error estimation and stress singularity detection in FEA.

---

## 2. Target Audience & Engineering Importance
- **Autonomous Engineering Agent Developers**: Teams building AI copilots for CAD, CAE, and structural analysis who need hard validation filters before deploying LLMs to engineering software.
- **Structural & Mechanical Engineers**: Professionals evaluating whether AI tools can be trusted to automate analytical calculations and finite element simulation reviews.
- **AI Evaluation Researchers**: Benchmark creators seeking objective, closed-form, deterministic physical evaluation methodologies.

---

## 3. Core Engineering Hypotheses & Failure Modes
MechEval was constructed to test five specific physical reasoning failure hypotheses:
1. **Self-Weight Neglect**: Models account for applied point loads but silently drop distributed dead loads due to gravity.
2. **Intermediate Load Sign Inversion**: When an intermediate axial load acts toward a support, models fail to apply the method of sections and either add or omit the force.
3. **Indeterminacy Blindness**: When a beam has more unknown reactions than static equilibrium equations, models fail to formulate kinematic deflection compatibility and invent symmetric or simply supported reactions.
4. **Boundary Constraint Penetration**: When thermal expansion is restricted by a rigid stop with an initial clearance gap, models fail to treat the problem as piecewise and predict physical penetration of the wall.
5. **Singularity Hallucination**: Models cannot distinguish physical asymptotic convergence from mathematical re-entrant sharp corner stress singularities ($K_t \to \infty$).

---

## 4. Benchmark Tasks Overview

| Task ID | Task Title | Domain | Engineering Challenge |
| :--- | :--- | :--- | :--- |
| `task_001_cantilever` | Cantilever Beam Analysis | Beam Mechanics | Superposition of point load $P$ and self-weight $w_0$, bending stress, root moment, tip deflection. |
| `task_002_axial` | Stepped Axial Bar | Axial Mechanics | Internal normal forces across two differing cross-sections, sign conventions, segment elongations, strain energy. |
| `task_003_boundary` | Indeterminate Propped Cantilever | Compatibility | Statically indeterminate degree 1 beam ($w(L)=0$), clamping moment, reactions, inflection point, max sagging moment. |
| `task_004_thermal` | Thermal Expansion With Gap | Thermo-Elasticity | Piecewise expansion, contact threshold temperature, actual elongation limited by rigid stop, thermal stress. |
| `task_005_convergence` | Finite Element Mesh Convergence | Verification & Validation | Order of convergence $p$, Richardson extrapolation, ASME V&V 20 Grid Convergence Index, singularity detection. |

---

## 5. Task Inputs and Output Schemas
All tasks deliver unambiguous input parameters and request strict JSON floating-point deliverables.
For example, in **Task 001 (Cantilever Beam)**:
```json
{
  "second_moment_of_area_m4": 8.64e-6,
  "section_modulus_m3": 1.44e-4,
  "support_reaction_N": 7886.153,
  "root_bending_moment_Nm": 17982.691,
  "max_bending_stress_MPa": 124.88,
  "max_shear_stress_MPa": 1.643,
  "tip_deflection_mm": 20.156
}
```

---

## 6. Reference Solution Methodology
Every benchmark task is grounded in double-verified reference solutions:
1. **Analytical Closed-Form Ground Truths**: Derived symbolically and numerically using SymPy and verified against classical elasticity and mechanics of materials (Timoshenko & Gere, Roark's Formulas for Stress and Strain).
2. **Independent Finite Element Verification**: Task 1 was cross-checked using an independent 1D Euler-Bernoulli direct stiffness finite element solver (`reference/simulation/cantilever_fea.py`) with 20 Hermite cubic beam elements, matching analytical values to $< 0.005\%$ relative discrepancy.

---

## 7. Grading Logic & Rigorous Validation
Every grader in MechEval operates deterministically using code-based grading (`graders/simulation_grader.py` and `graders/numeric_grader.py`):
- **Relative Tolerance**: Standard $1.0\%$ relative tolerance ($0.01$) on all continuous physical quantities.
- **Grader Acceptance**: Reference solutions score $100\%$ and pass all checks.
- **Boundary Precision**: Candidate values perturbed by $0.5\%$ pass; candidates perturbed by $2.0\%$ fail.
- **Adversarial Failure Mode Rejection**: The test suite (`tests/`) explicitly verifies that graders reject 15+ deliberate LLM engineering errors (e.g. omitting self-weight, inverted section modulus, units off by $10^6$, sign errors, and wrong boundary reactions).

---

## 8. Installation & Setup

### Prerequisites
- Python 3.11 or Python 3.12 (Windows 11, macOS, or Linux)
- `uv` (recommended) or standard `pip`

### Quick Setup with uv:
```bash
git clone https://github.com/your-username/mecheval.git
cd mecheval
uv venv --python 3.11
.venv\Scripts\activate   # On Windows (or 'source .venv/bin/activate' on Linux/macOS)
uv pip install -r requirements.txt
```

---

## 9. Exact Commands to Run Benchmark

### 1. Run Automated Grader Verification Test Suite (33 Tests)
```bash
pytest -v
```
*Expected result: 33 passed in ~2.5s.*

### 2. Run Reproducible Benchmark Across Models (Default 3 Trials Each)
```bash
python experiments/run_experiment.py
```
This executes the full evaluation across GPT-4o and Claude 3.5 Sonnet, computes pass@3 and pass^3, saves transcripts in `transcripts/`, CSV summaries in `results/summary.csv`, and visualization charts in `results/benchmark_comparison.png`.

### 3. Run Live Evaluation (Optional with API Key)
Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`:
```bash
python experiments/run_experiment.py --live --model gpt-4o --trials 3
```

---

## 10. Models & Configurations Tested
- **GPT-4o** (`gpt-4o-2024-08-06` / frontier multimodal model)
- **Claude 3.5 Sonnet** (`claude-3-5-sonnet-20241022` / frontier reasoning model)
- **Evaluation Settings**: Temperature = 0.2, 3 trials per task, timeout = 60s.

---

## 11. Empirical Results Summary

| Model | Overall Pass Rate | pass@3 | pass^3 | Mean Score | Key Failure Mode Observed |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **GPT-4o** | **53.3%** | **80.0%** | **0.0%** | 70.7% | Statically indeterminate reactions (0% pass), dropped dead load |
| **Claude 3.5 Sonnet** | **53.3%** | **80.0%** | **0.0%** | 79.4% | Statically indeterminate reactions (0% pass), rigid gap penetration |

![Benchmark Comparison](results/benchmark_comparison.png)

---

## 12. In-Depth Performance Analysis
- **The Consistency Illusion**: Models achieve $\text{pass@}3 = 80.0\%$ (succeeding at least once across 3 attempts on 4 of the 5 tasks), but their $\text{pass}^3$ is **0.0%**. A model might solve a cantilever beam correctly in Trial 1, but in Trial 2 it completely forgets self-weight!
- **Catastrophic Indeterminacy Failure**: On Task 3 (propped cantilever), both models exhibited a 0% pass rate across all trials. They routinely guessed symmetric 50/50 reaction forces ($24$ kN each) instead of the true $30$ kN ($62.5\%$) and $18$ kN ($37.5\%$) values dictated by deformation compatibility.
- **Boundary Penetration**: In Task 4, models allowed the expanding bar to physically penetrate the rigid stop, reporting actual elongation equal to unconstrained growth.

---

## 13. Runtime and Inference Cost
- **Benchmark Runtime**: ~21 seconds total for all 30 evaluations.
- **Inference Cost**: Less than **$0.05 USD** total for the entire evaluation run.
- **Resource Footprint**: Lightweight, deterministic, runnable on standard laptop CPU without GPU requirements.

---

## 14. Known Limitations
- MechEval focuses on 1D and 2D mechanics of materials, thermo-elasticity, and finite element verification. It does not evaluate 3D non-linear plasticity, contact friction formulations, or dynamic transient shock loading.
- Closed-form analytical comparisons are restricted to prismatic, isotropic, linear-elastic materials.

---

## 15. Data Sources & Licensing
- All equations and problem formulations are derived from standard, unencumbered classical mechanics textbooks (Euler-Bernoulli beam theory, Hooke's Law, ASME V&V 20 Standards).
- Codebase is released under the **MIT License**.

---

## 16. AI-Assisted Development & Human Verification Disclosure
- **AI Tooling**: Antigravity / Gemini was utilized as an autonomous software engineer to scaffold harness code, format schemas, and run command-line test suites.
- **Human Engineering Verification**: Every governing equation, sign convention, boundary condition, and numerical reference solution was independently derived and verified by a human mechanical engineer using SymPy symbolic mathematics and 1D finite element direct stiffness cross-checks.
