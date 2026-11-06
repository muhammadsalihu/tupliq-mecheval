"""
MechEval Benchmark Experiment Runner.
Executes multi-trial benchmark evaluations across models, computes pass@k and pass^k,
generates CSV summaries and comparison visualizations.
"""

import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# Ensure root dir in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.task_001_cantilever.task import CantileverBeamTask
from tasks.task_002_axial.task import SteppedAxialBarTask
from tasks.task_003_boundary.task import ProppedCantileverTask
from tasks.task_004_thermal.task import ThermalExpansionGapTask
from tasks.task_005_convergence.task import MeshConvergenceTask

from evaluator.model_adapter import OfflineReplayModelAdapter, LiveAPIModelAdapter
from evaluator.recorded_trials import GPT4O_TRIALS, CLAUDE35_TRIALS
from evaluator.runner import BenchmarkRunner
from evaluator.metrics import BenchmarkMetrics


def get_all_tasks():
    return [
        CantileverBeamTask(),
        SteppedAxialBarTask(),
        ProppedCantileverTask(),
        ThermalExpansionGapTask(),
        MeshConvergenceTask(),
    ]


def run_benchmark_for_model(model_name: str, num_trials: int = 3, use_live_api: bool = False):
    tasks = get_all_tasks()

    if use_live_api:
        adapter = LiveAPIModelAdapter(model_name=model_name)
    else:
        # Use recorded real empirical trials
        if "claude" in model_name.lower():
            trials_data = CLAUDE35_TRIALS
            clean_name = "claude-3-5-sonnet"
        else:
            trials_data = GPT4O_TRIALS
            clean_name = "gpt-4o"
        adapter = OfflineReplayModelAdapter(model_name=clean_name, trial_records=trials_data)

    runner = BenchmarkRunner(
        tasks=tasks,
        adapter=adapter,
        num_trials=num_trials,
        transcripts_dir="transcripts",
        results_dir="results/raw",
    )

    records = runner.run_benchmark()
    summary = BenchmarkMetrics.compute_summary(records)
    return summary


def generate_benchmark_charts(summaries: list, output_image_path: str = "results/benchmark_comparison.png"):
    """Generates comparison bar chart between models across all tasks."""
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

    tasks = [t["task_id"].replace("task_", "").replace("_", " ").title() for t in summaries[0]["task_breakdown"]]
    n_tasks = len(tasks)
    n_models = len(summaries)

    plt.figure(figsize=(12, 6))
    bar_width = 0.35
    indices = range(n_tasks)

    for i, s in enumerate(summaries):
        model_name = s["model_name"]
        pass_rates = [t["pass_rate"] * 100.0 for t in s["task_breakdown"]]
        offset = (i - (n_models - 1) / 2.0) * bar_width
        plt.bar([idx + offset for idx in indices], pass_rates, width=bar_width, label=model_name, alpha=0.85)

    plt.xlabel("Engineering Evaluation Task", fontsize=11, fontweight="bold")
    plt.ylabel("Pass Rate (%)", fontsize=11, fontweight="bold")
    plt.title("MechEval: AI Mechanical Engineering Benchmark Performance Comparison", fontsize=13, fontweight="bold")
    plt.xticks(indices, tasks, rotation=15, ha="right")
    plt.ylim(0, 105)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    plt.close()
    print(f"[+] Comparison visualization saved to: {output_image_path}")


def main():
    parser = argparse.ArgumentParser(description="MechEval AI Mechanical Engineering Benchmark Runner")
    parser.add_argument("--trials", type=int, default=3, help="Number of trials per task (default: 3)")
    parser.add_argument("--live", action="store_true", help="Run against live LLM API instead of reproducible offline trials")
    parser.add_argument("--model", type=str, default="all", help="Model to evaluate (gpt-4o, claude-3-5-sonnet, or all)")
    args = parser.parse_args()

    models_to_run = ["gpt-4o", "claude-3-5-sonnet"] if args.model == "all" else [args.model]

    summaries = []
    combined_rows = []

    print("\n" + "="*70)
    print("MECHEVAL: MECHANICAL ENGINEERING AI EVALUATION BENCHMARK")
    print(f"Executing {len(models_to_run)} model(s) across 5 engineering tasks, {args.trials} trials each.")
    print("="*70 + "\n")

    for model_name in models_to_run:
        print(f"[*] Evaluating Model: {model_name}...")
        summary = run_benchmark_for_model(model_name, num_trials=args.trials, use_live_api=args.live)
        summaries.append(summary)

        df = BenchmarkMetrics.to_dataframe(summary["task_breakdown"])
        df.insert(0, "Model", summary["model_name"])
        combined_rows.append(df)

        print(f"    - Pass Rate:      {summary['overall_pass_rate']:.1%}")
        print(f"    - pass@3:         {summary['overall_pass@k']:.1%}")
        print(f"    - pass^3:         {summary['overall_pass^k']:.1%}")
        print(f"    - Mean Score:     {summary['overall_mean_score']:.1%}")
        print(f"    - Total Runtime:  {summary['total_runtime_s']:.2f}s\n")

    # Combine and save CSV summaries
    full_df = pd.concat(combined_rows, ignore_index=True)
    os.makedirs("results/processed", exist_ok=True)
    csv_path = "results/summary.csv"
    full_df.to_csv(csv_path, index=False)
    print(f"[+] Consolidated summary CSV saved to: {csv_path}")

    # Generate charts
    generate_benchmark_charts(summaries, "results/benchmark_comparison.png")

    print("\n" + "="*70)
    print("BENCHMARK EXECUTION SUMMARY TABLE")
    print("="*70)
    print(full_df.to_string(index=False))
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
