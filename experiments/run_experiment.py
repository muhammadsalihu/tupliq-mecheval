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

# Optional .env support (python-dotenv is in requirements.txt) so the API key can live in .env
# instead of the shell. Absent package or absent file is fine — the environment still works.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from tasks.task_001_cantilever.task import CantileverBeamTask
from tasks.task_002_axial.task import SteppedAxialBarTask
from tasks.task_003_boundary.task import ProppedCantileverTask
from tasks.task_004_thermal.task import ThermalExpansionGapTask
from tasks.task_005_convergence.task import MeshConvergenceTask

from evaluator.model_adapter import LiveAPIModelAdapter, ModelUnavailableError
from evaluator.runner import BenchmarkRunner
from evaluator.metrics import BenchmarkMetrics
from evaluator.model_registry import (
    ROSTER, resolve, validate_roster, UnknownModelError,
    base_url, models_url, fetch_catalogue, pricing_map,
)

# Frontier cheap models evaluated live. Short names resolve through evaluator.model_registry to
# fully-qualified model ids; the endpoint and its catalogue come from the environment.
DEFAULT_MODELS = list(ROSTER)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_all_tasks():
    return [
        CantileverBeamTask(),
        SteppedAxialBarTask(),
        ProppedCantileverTask(),
        ThermalExpansionGapTask(),
        MeshConvergenceTask(),
    ]


def run_benchmark_for_model(model_name: str, num_trials: int = 3, use_live_api: bool = True, pricing: dict | None = None):
    tasks = get_all_tasks()

    if not use_live_api:
        raise ValueError(
            "Replayed/hand-written trial data is no longer supported. "
            "MechEval results must come from real API runs (--live)."
        )
    adapter = LiveAPIModelAdapter(model_name=model_name, base_url=base_url(), pricing=pricing)

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
    parser.add_argument("--live", action="store_true", help="Run against live LLM API (required)", default=True)
    parser.add_argument("--models", type=str, default="all", help="Comma-separated model list, or 'all' for the default roster")
    parser.add_argument("--validate-models", action="store_true",
                        help="Resolve every slug against OpenRouter's catalogue and exit (no API key needed)")
    parser.add_argument("--allow-unknown", action="store_true",
                        help="Skip the catalogue preflight (an unknown slug otherwise aborts the run)")
    args = parser.parse_args()

    if args.models == "all":
        models_to_run = DEFAULT_MODELS
    else:
        models_to_run = [m.strip() for m in args.models.split(",") if m.strip()]

    # Short name -> provider-prefixed OpenRouter slug. A typo aborts here, never mid-run.
    try:
        resolved = [resolve(m) for m in models_to_run]
    except UnknownModelError as exc:
        print(f"[!] {exc}")
        sys.exit(2)
    for short, slug in zip(models_to_run, resolved):
        print(f"[i] model '{short}' -> '{slug}'")

    unknown = validate_roster(resolved)
    if unknown:
        print(f"[!] Not in OpenRouter's catalogue: {unknown}")
        if not args.allow_unknown:
            print("[!] Aborting before spending tokens. Fix the slug or pass --allow-unknown.")
            sys.exit(2)
    else:
        print("[+] All slugs present in OpenRouter's catalogue.")
    if args.validate_models:
        return
    models_to_run = resolved

    summaries = []
    combined_rows = []

    print("\n" + "="*70)
    print("MECHEVAL: MECHANICAL ENGINEERING AI EVALUATION BENCHMARK")
    print(f"Endpoint: {base_url()}")
    print(f"Executing {len(models_to_run)} model(s) across 5 engineering tasks, {args.trials} trials each.")
    print("="*70 + "\n")

    # The endpoint's own catalogue: proves the ids exist and supplies the prices the cost column uses.
    catalogue = fetch_catalogue()
    prices = pricing_map(catalogue)

    for model_name in models_to_run:
        print(f"[*] Evaluating Model: {model_name}...")
        summary = run_benchmark_for_model(model_name, num_trials=args.trials, use_live_api=args.live,
                                          pricing=prices)
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

    # Provenance for the results: which endpoint and roster produced this file, so a reader never
    # has to guess (and so a stale results set is detectable).
    import json as _json
    from evaluator.model_registry import label_for
    meta = {
        "endpoint": base_url(),
        "catalogue_url": models_url(),
        "models": models_to_run,
        "labels": {m: label_for(m) for m in models_to_run},
        "trials_per_task": args.trials,
        "tasks": [t["task_id"] for t in summaries[0]["task_breakdown"]] if summaries else [],
        "pricing_usd_per_token": {m: prices.get(m) for m in models_to_run},
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }
    os.makedirs("results", exist_ok=True)
    with open("results/run_environment.json", "w", encoding="utf-8") as fh:
        _json.dump(meta, fh, indent=2)
    print(f"[+] Run provenance written to results/run_environment.json (endpoint {meta['endpoint']})")


if __name__ == "__main__":
    main()
