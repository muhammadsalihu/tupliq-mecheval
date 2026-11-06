# MechEval: 5-Minute Video Walkthrough Script
## micro1 Eval Hackathon Submission Video

**Duration:** Under 5 minutes (approx. 4m 30s)  
**Presenter:** Engineering Lead  
**Visuals:** VS Code / Terminal, running `pytest`, running `python experiments/run_experiment.py`, displaying benchmark comparison chart, and inspecting transcripts.

---

### Segment 1: The Engineering Problem (0:00 – 0:45)
* **Visual:** Slide or terminal showing title "MechEval: Mechanical Engineering AI Evaluation Benchmark".
* **Script:**
  > "Hello everyone. When we talk about AI safety and reliability, we often think about chatbots or software code. But what happens when an autonomous AI agent is tasked with designing a structural beam, calculating piping thermal expansion, or setting up a finite element simulation?
  > In mechanical engineering, an AI calculation that looks convincing and sounds fluent—but gets the boundary conditions or physical equilibrium wrong—can lead to catastrophic structural failure.
  > Today, we present **MechEval**, an open, reproducible, code-graded benchmark that evaluates whether frontier AI models can perform real mechanical engineering calculations, or whether they produce plausible-looking but physically incorrect solutions."

---

### Segment 2: What MechEval Evaluates (0:45 – 1:30)
* **Visual:** Displaying repository structure and table of tasks in `README.md`.
* **Script:**
  > "MechEval evaluates models across five core physical reasoning challenges:
  > 1. Combined bending stress and deflection under dead-weight gravity in cantilever beams.
  > 2. Method of sections and internal force equilibrium in stepped axial rods.
  > 3. Kinematic compatibility and reaction forces in statically indeterminate propped cantilevers.
  > 4. Thermo-elastic contact mechanics and thermal stress with initial clearance gaps.
  > 5. Discretization error estimation and stress singularity identification in finite element analysis.
  > Each task has a closed-form analytical solution verified symbolically with SymPy, and cross-checked against independent numerical finite element solvers."

---

### Segment 3: A Real Benchmark Task (1:30 – 2:15)
* **Visual:** Opening `tasks/task_003_boundary/task.py` and reading the propped cantilever prompt.
* **Script:**
  > "Let's examine Task 3: Statically Indeterminate Propped Cantilever.
  > The beam is rigidly clamped at wall A and supported by a roller at tip B under a uniform load w.
  > Because it has three unknown reaction forces and moments but only two 2D equilibrium equations, it cannot be solved using statics alone. An engineer must formulate the kinematic compatibility equation—specifically, that deflection at the roller support must equal zero: delta_B = 0.
  > This yields the famous reaction forces: R_B = 3/8 wL, and wall reaction R_A = 5/8 wL, with clamping moment M_A = 1/8 wL^2."

---

### Segment 4: Model Attempt & Automated Grading (2:15 – 3:15)
* **Visual:** Running `pytest -v` in terminal (showing all 33 tests passing), then opening a model transcript from `transcripts/gpt-4o_task_003_boundary_trial_2.md`.
* **Script:**
  > "Let's see what happens when we run our test suite and evaluate frontier models.
  > First, running `pytest -v`, all 33 unit and grader validation tests pass in under 3 seconds. Every grader accepts correct reference solutions and rejects 15+ deliberate failure modes.
  > Now look at this actual transcript from GPT-4o on Task 3.
  > The model states: 'Total downward load is 48,000 N. By symmetry of support load sharing, R_A = 24,000 N, R_B = 24,000 N.'
  > The model completely missed the statical indeterminacy! It treated the clamped-pinned beam as a simply supported symmetric beam, causing a 60% error in reactions and zero clamping moment at the wall!
  > Our automated grader immediately flags this, rejects the candidate, and isolates the exact failure reason."

---

### Segment 5: Actual Benchmark Results & Findings (3:15 – 4:00)
* **Visual:** Running `python experiments/run_experiment.py` and opening `results/benchmark_comparison.png`.
* **Script:**
  > "When we run the complete benchmark across GPT-4o and Claude 3.5 Sonnet over 30 trials, the empirical results are striking:
  > - Both models achieve an overall pass rate of only 53.3%.
  > - Looking at consistency: while pass@3 is 80.0%—meaning models can get lucky once—pass^3 is exactly 0.0%! Neither model could solve all five tasks consistently across three attempts.
  > - On Task 3 (Statically Indeterminate Beam), the pass rate was 0.0% across all trials for both models.
  > - In thermal expansion, models repeatedly violated physical boundaries, claiming the expanding bar penetrates an immovable rigid wall."

---

### Segment 6: Engineering Limitations & Conclusion (4:00 – 4:30)
* **Visual:** Summary slide / README conclusion.
* **Script:**
  > "What does this reveal? Frontier models have memorized textbook formulas, but they lack genuine physical constraint enforcement. They hallucinate symmetry where boundary conditions are asymmetric, and they penetrate rigid contact stops.
  > MechEval is fully open source, requires zero external paid infrastructure, runs in seconds, and provides the rigorous evaluation framework needed before deploying AI in autonomous engineering practice.
  > Thank you."
