# MechEval: Mechanical Engineering AI Evaluation Benchmark

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 33 Passed](https://img.shields.io/badge/Tests-33%20Passed-brightgreen.svg)](tests/)
[![Eval: micro1 Hackathon](https://img.shields.io/badge/micro1-Eval%20Hackathon%202026-orange.svg)]()

> **MechEval** is a reproducible, code-graded AI evaluation benchmark that rigorously exposes physical reasoning limitations in frontier AI models performing professional mechanical and structural engineering tasks.

---

## Demo video

**[Watch the MechEval walkthrough →](https://youtu.be/9wNIa13TxZU)** — https://youtu.be/9wNIa13TxZU

2:23, narrated. It walks the five tasks, the live model roster, the measured results and the
failure modes the graders recorded, and ends with the exact reproduction commands. Every figure
shown in it is read from the run's own `results/raw/*.json`, so the video cannot quote a model or a
number the run did not produce.

---

## Table of Contents
0. [Demo video](#demo-video)
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
Frontier AI models can rapidly generate plausible-looking engineering derivations. However, in safety-critical physical systems (civil infrastructure, aerospace airframes, high-pressure piping, and machinery), a calculation that looks convincing but is physically invalid can cause structural collapse and catastrophic failure. Related work on LLM-assisted simulation setup — Shafiq, Ghiassi & Alexiadis, *"The Power of Small LLMs in Geometry Generation for Physical Simulations"* (University of Birmingham) — shows LLMs can generate GMSH simulation inputs, which raises the complementary question MechEval answers: can these models be trusted to get the physics of the inputs *right*?

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
git clone https://github.com/muhammadsalihu/tupliq-mecheval.git
cd tupliq-mecheval
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
Copy `.env.example` to `.env` and set your `OPENROUTER_API_KEY`, then:
```bash
python experiments/run_experiment.py --trials 3
```
This executes the full live evaluation across the default model roster (GPT-6 Luna, DeepSeek 4.1 Flash, GLM 5.3 Flash, Haiku 5.5), computes pass@3 and pass^3, saves transcripts in `transcripts/`, CSV summaries in `results/summary.csv`, and visualization charts in `results/comparison.png`. The endpoint is the OpenAI-compatible base URL in `MECHEVAL_BASE_URL` (default `https://openrouter.ai/api/v1`); every run writes the endpoint, roster and prices it used to `results/run_environment.json`.

### 3. Run a Single Model
```bash
python experiments/run_experiment.py --models deepseek-4.1-flash --trials 3
```

---

## 10. Models & Configurations Tested
Evaluated live via OpenRouter (`https://openrouter.ai/api/v1`), temperature = 0.2, 3 trials per task, timeout = 60 s:
- **GPT-6 Luna** — `openai/gpt-6-luna` (short name `gpt-6-luna`)
- **DeepSeek 4.1 Flash** — `deepseek/deepseek-v4.1-flash` (short name `deepseek-4.1-flash`)
- **GLM 5.3 Flash** — `z-ai/glm-5.3-flash` (short name `glm-5.3-flash`)
- **Haiku 5.5** — `anthropic/claude-haiku-5.5` (short name `haiku-5.5` — cheapest Claude-class model at evaluation time)

Short names resolve to the slugs above through `evaluator/model_registry.py`. Every slug is
checked against OpenRouter's catalogue before a run starts (`python experiments/run_experiment.py
--validate-models`, no API key needed); a slug the provider does not serve — or one it rejects at
request time — aborts the run instead of being scored as the model failing the task.

---

## 11. Empirical Results Summary

Live trials: **4 models × 5 tasks × 3 trials = 60 calls**, temperature 0.2, endpoint
`https://inference-api.nousresearch.com/v1` (OpenAI-compatible; prices read from that endpoint's
own catalogue). Run provenance — endpoint, roster, prices, timestamp — is written to
`results/run_environment.json`, and every figure below is reproduced by
`python reports/generate_report.py` from `results/summary.csv` and `results/raw/*.json`.

| Model | Trials | Passed | Pass rate | pass@k | pass^k | Mean score | Mean latency | Recorded cost |
|---|---|---|---|---|---|---|---|---|
| GPT-6 Luna (`openai/gpt-6-luna`) | 15 | 9 | 60.0% | 60% | 60% | 80.7% | 9.2 s | $0.0073 |
| DeepSeek 4.1 Flash (`deepseek/deepseek-v4.1-flash`) | 15 | 9 | 60.0% | 60% | 60% | 82.1% | 67.4 s | $0.0563 |
| Haiku 5.5 (`anthropic/claude-haiku-5.5`) | 15 | 9 | 60.0% | 60% | 60% | 82.1% | 8.3 s | $0.0146 |
| GLM 5.3 Flash (`z-ai/glm-5.3-flash`) | 15 | 5 | 33.3% | 40% | 20% | 66.3% | 101.3 s | $0.0393 |

Definitions: pass rate = trials passed / trials run; pass@k = share of tasks with at least one
passing trial; pass^k = share of tasks where every trial passed. Total recorded spend for all 60
calls: **$0.1174**.

Per task (passed / 3 trials):

| Task | GPT-6 Luna | DeepSeek 4.1 Flash | GLM 5.3 Flash | Haiku 5.5 |
|---|---|---|---|---|
| 1 · Cantilever under point load + self-weight | 3/3 | 3/3 | 2/3 | 3/3 |
| 2 · Stepped axial bar under intermediate load | 3/3 | 3/3 | 3/3 | 3/3 |
| 3 · Statically indeterminate propped cantilever | 0/3 | 0/3 | 0/3 | 0/3 |
| 4 · Constrained thermal expansion vs. clearance gap | 0/3 | 0/3 | 0/3 | 0/3 |
| 5 · FEA mesh convergence / singularity detection | 3/3 | 3/3 | 0/3 \* | 3/3 |

\* GLM 5.3 Flash at task 5: two of the three trials exceeded the 420 s read timeout — a harness
transport failure, not model reasoning — and the third failed the grader at a 27.5% mean score.

---

## 12. In-Depth Performance Analysis

**Two tasks are failed by every model, in every trial.** Across all four models, task 3 (propped
cantilever) and task 4 (thermal expansion against a gap) are **0/12 trials each**. The failing
checks are specific rather than diffuse: `reaction_force_N`, `max_positive_moment_Nm` and
`max_deflection_mm` on task 3; `free_thermal_expansion_mm`, `temperature_to_close_gap_C`,
`restrained_expansion_mm` and `thermal_stress_MPa` on task 4.

**The thermal failures share one signature.** All four models under-predict every *restrained*
quantity in task 4 by the same small margin — in the trials sampled, GPT-6 Luna returns restrained
expansion 1.095 mm vs a 1.135 mm reference, thermal stress 140.89 MPa vs 146.10 MPa and reaction
225.4 kN vs 233.8 kN: **3.57% low on all three**, against a 1% tolerance. One rounded material
constant reproduces that pattern across force, stress and displacement simultaneously; a wrong
governing model does not. The same models get the *unconstrained* elongation right
(`actual_elongation_mm`, 0.0% relative error, check passed) and lose the task on the quantities
that depend on the elastic constant once the gap closes.

**Task 3 is a failure of method, not arithmetic.** Every attempt reports reactions close to the
simply-supported split instead of solving the compatibility equation, which is why the moment and
deflection checks fail together while the determinate axial task in the same family passes 3/3.

**Consistency is binary on this roster, not probabilistic.** For GPT-6 Luna, DeepSeek 4.1 Flash and
Haiku 5.5, pass@k = pass^k = 60%: every trial on tasks 1, 2 and 5 passes, every trial on tasks 3
and 4 fails. No model is lucky once and wrong the next time on the same task — MechEval separates
capability from sampling, and nothing here sits in between. GLM 5.3 Flash is the exception
(pass@k 40% vs pass^k 20%), driven by task 1 (2/3) and the timed-out task 5 trials.

**Accuracy does not track speed or price.** Haiku 5.5 (8.3 s mean, $0.0146) matches DeepSeek 4.1
Flash (67.4 s, $0.0563) and GPT-6 Luna (9.2 s, $0.0073) on every task boundary, while GLM 5.3
Flash is both the slowest (101.3 s mean, two 420 s timeouts) and the weakest (33.3% pass rate).

---

## 13. Runtime and Inference Cost

Measured on the run in Section 11 (60 live calls, 4 models × 5 tasks × 3 trials):

| Model | Wall-clock, 15 trials | Mean latency | Recorded cost |
|---|---|---|---|
| Haiku 5.5 | 124.4 s | 8.3 s | $0.0146 |
| GPT-6 Luna | 138.2 s | 9.2 s | $0.0073 |
| DeepSeek 4.1 Flash | 1011.0 s | 67.4 s | $0.0563 |
| GLM 5.3 Flash | 1520.1 s | 101.3 s | $0.0393 |
| **Total** | **~46.6 min** | — | **$0.1174** |

- Cost is computed per call from the endpoint's published price for the model actually called; the
  price table used is recorded in `results/run_environment.json`. No per-1M constants are hardcoded.
- Read timeout is 300 s by default, 420 s for this run (`MECHEVAL_TIMEOUT`); two GLM 5.3 Flash
  trials still exceeded it and are recorded as adapter errors in `results/raw/`.
- Wall-clock is dominated by two models: DeepSeek 4.1 Flash and GLM 5.3 Flash account for ~91% of
  the sweep duration and ~81% of its spend.

---

## 14. Known Limitations
- MechEval focuses on 1D and 2D mechanics of materials, thermo-elasticity, and finite element verification. It does not evaluate 3D non-linear plasticity, contact friction formulations, or dynamic transient shock loading.
- Closed-form analytical comparisons are restricted to prismatic, isotropic, linear-elastic materials.
- **Transport vs. reasoning.** Two GLM 5.3 Flash trials (task 5) hit the 420 s read timeout and are recorded as adapter errors, not reasoning failures. Its task-5 column (0/3) therefore mixes one graded failure with two harness timeouts; the headline pass rate for that model should be read with that in mind.
- **Snapshot, not a leaderboard.** These are 3 trials per task on one endpoint at one point in time. Model versions change behind the same id; re-run `experiments/run_experiment.py --trials 3` to refresh rather than quoting this table indefinitely.

---

## 15. Data Sources & Licensing
- All equations and problem formulations are derived from standard, unencumbered classical mechanics textbooks (Euler-Bernoulli beam theory, Hooke's Law, ASME V&V 20 Standards).
- Task 5 (mesh convergence / geometry-to-GMSH verification) is motivated by recent work on LLM-assisted simulation setup: **Shafiq, O., Ghiassi, B., & Alexiadis, A. — "The Power of Small LLMs in Geometry Generation for Physical Simulations"** (University of Birmingham), which demonstrates LoRA fine-tuned small LLMs (Phi-3 Mini, Qwen-2.5 1.5B) generating precise GMSH engineering geometries and outperforming GPT-4o on this specialized task. MechEval complements that line of work by measuring whether general frontier models can verify — not just generate — simulation inputs against physical ground truths.
- Codebase is released under the **MIT License**.

---

## 16. AI-Assisted Development & Human Verification Disclosure
- **AI Tooling**: Antigravity / Gemini was utilized as an autonomous software engineer to scaffold harness code, format schemas, and run command-line test suites.
- **Human Engineering Verification**: Every governing equation, sign convention, boundary condition, and numerical reference solution was independently derived and verified by a human mechanical engineer using SymPy symbolic mathematics and 1D finite element direct stiffness cross-checks.
