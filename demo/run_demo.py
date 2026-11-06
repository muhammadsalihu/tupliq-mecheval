"""
MechEval Interactive CLI Demonstration.
Quickly showcases an engineering task prompt, evaluates reference vs flawed AI attempts,
and prints live grading verdicts.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.task_001_cantilever.task import CantileverBeamTask
from tasks.task_003_boundary.task import ProppedCantileverTask


def main():
    print("\n" + "="*70)
    print("MECHEVAL INTERACTIVE LIVE DEMONSTRATION")
    print("Mechanical Engineering AI Physical Reasoning Benchmark")
    print("="*70 + "\n")

    # Demo 1: Cantilever Beam Task
    task1 = CantileverBeamTask()
    print(">>> DEMO 1: Cantilever Beam with Tip Load & Self-Weight (Task 001)")
    print("Ground Truth Reference Calculation:")
    ref1 = task1.get_reference_solution()
    for k, v in ref1.items():
        print(f"  - {k}: {v}")

    print("\nEvaluating Flawed AI Solution (Model forgets beam self-weight):")
    flawed_cantilever = dict(ref1)
    flawed_cantilever["root_bending_moment_Nm"] = 16250.0  # P*L only, missing w0*L^2/2
    flawed_cantilever["support_reaction_N"] = 6500.0       # P only
    flawed_cantilever["max_bending_stress_MPa"] = 112.85
    flawed_cantilever["tip_deflection_mm"] = 18.67

    report1 = task1.grade(flawed_cantilever)
    print(f"Grader Verdict: Passed = {report1.all_passed}, Score = {report1.score:.1%}")
    print("Failure Reasons Flagged by Grader:")
    for f in report1.failure_reasons:
        print(f"  [X] {f}")

    print("\n" + "-"*70 + "\n")

    # Demo 2: Statically Indeterminate Beam
    task3 = ProppedCantileverTask()
    print(">>> DEMO 2: Statically Indeterminate Propped Cantilever (Task 003)")
    print("Ground Truth Compatibility Reference Calculation:")
    ref3 = task3.get_reference_solution()
    for k, v in ref3.items():
        print(f"  - {k}: {v}")

    print("\nEvaluating Common AI Hallucination (Model assumes symmetric 50/50 load sharing):")
    hallucinated_propped = dict(ref3)
    hallucinated_propped["roller_reaction_N"] = 24000.0
    hallucinated_propped["wall_vertical_reaction_N"] = 24000.0
    hallucinated_propped["wall_moment_Nm"] = 0.0

    report3 = task3.grade(hallucinated_propped)
    print(f"Grader Verdict: Passed = {report3.all_passed}, Score = {report3.score:.1%}")
    print("Failure Reasons Flagged by Grader:")
    for f in report3.failure_reasons:
        print(f"  [X] {f}")

    print("\n" + "="*70)
    print("Demo completed successfully. Run 'pytest -v' for full test suite.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
