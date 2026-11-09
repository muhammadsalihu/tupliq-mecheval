"""
Renders reports/benchmark_report.md from a completed run.

Every number here is read from the run's own artifacts — results/summary.csv,
results/raw/*.json and results/run_environment.json — so the report cannot drift from the trials,
and a report that quotes a roster or endpoint the run did not use is impossible to produce.
"""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SUMMARY = os.path.join(BASE_DIR, "results", "summary.csv")
RAW_DIR = os.path.join(BASE_DIR, "results", "raw")
ENVIRONMENT = os.path.join(BASE_DIR, "results", "run_environment.json")
OUT = os.path.join(BASE_DIR, "reports", "benchmark_report.md")


def _load_summary():
    with open(SUMMARY, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_raw():
    records = {}
    if not os.path.isdir(RAW_DIR):
        return records
    for name in sorted(os.listdir(RAW_DIR)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(RAW_DIR, name), encoding="utf-8") as fh:
            records[name[:-len("_raw_results.json")]] = json.load(fh)
    return records


def _load_environment():
    if os.path.exists(ENVIRONMENT):
        with open(ENVIRONMENT, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _pct(value) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "n/a"


def build_report() -> str:
    rows = _load_summary()
    raw = _load_raw()
    env = _load_environment()

    models = []
    for row in rows:
        if row["Model"] not in models:
            models.append(row["Model"])
    tasks = [r["Task ID"] for r in rows if r["Model"] == models[0]] if models else []

    total_trials = sum(int(r["Trials"]) for r in rows)
    total_cost = 0.0
    for name, records in raw.items():
        total_cost += sum(float(rec.get("estimated_cost_usd") or 0.0) for rec in records)
    latencies = [float(rec.get("latency_seconds") or 0.0) for records in raw.values() for rec in records]
    adapter_errors = [
        (name, rec.get("adapter_error"))
        for name, records in raw.items()
        for rec in records
        if rec.get("adapter_error")
    ]

    lines = []
    lines.append("# MechEval Benchmark Report")
    lines.append("")
    lines.append("Generated from live trials by `python reports/generate_report.py`. "
                 "Every figure in this report is read from `results/summary.csv`, "
                 "`results/raw/*.json` and `results/run_environment.json`.")
    lines.append("")
    lines.append("## Run environment")
    lines.append("")
    lines.append(f"- **Endpoint**: `{env.get('endpoint', 'unknown')}`")
    lines.append(f"- **Models**: {', '.join(f'`{m}`' for m in env.get('models', models)) or 'n/a'}")
    lines.append(f"- **Trials per task**: {env.get('trials_per_task', 'n/a')}")
    lines.append(f"- **Trials recorded**: {total_trials}")
    lines.append(f"- **Recorded spend** (sum of per-call `estimated_cost_usd`): ${total_cost:.4f}")
    if latencies:
        lines.append(f"- **Latency**: mean {sum(latencies) / len(latencies):.1f}s, "
                     f"min {min(latencies):.1f}s, max {max(latencies):.1f}s")
    if env.get("generated_at_utc"):
        lines.append(f"- **Run completed**: {env['generated_at_utc']}")
    lines.append("")

    lines.append("## Headline results")
    lines.append("")
    lines.append("Aggregated from the trial records in `results/raw/` — pass rate = trials passed / trials run; "
                 "pass@k = share of tasks with at least one passing trial; pass^k = share of tasks where every "
                 "trial passed.")
    lines.append("")
    lines.append("| Model | Trials | Passed | Pass rate | pass@k | pass^k | Mean score | Mean latency (s) | Cost (USD) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for name, records in raw.items():
        if not records:
            continue
        # Raw files are named with the id flattened for the filesystem; show the real id.
        display = next((m for m in env.get("models", []) if m.replace("/", "-") == name), name)
        n = len(records)
        passed = sum(1 for rec in records if rec.get("all_passed"))
        by_task = defaultdict(list)
        for rec in records:
            by_task[rec.get("task_id")].append(bool(rec.get("all_passed")))
        at_least_one = sum(1 for fl in by_task.values() if any(fl)) / len(by_task) if by_task else 0.0
        all_pass = sum(1 for fl in by_task.values() if all(fl)) / len(by_task) if by_task else 0.0
        mean_score = sum(float(rec.get("score") or 0.0) for rec in records) / n
        mean_lat = sum(float(rec.get("latency_seconds") or 0.0) for rec in records) / n
        cost = sum(float(rec.get("estimated_cost_usd") or 0.0) for rec in records)
        lines.append(
            f"| `{display}` | {n} | {passed} | {passed / n * 100:.1f}% | {at_least_one * 100:.1f}% "
            f"| {all_pass * 100:.1f}% | {mean_score * 100:.1f}% | {mean_lat:.1f} | ${cost:.4f} |"
        )
    lines.append("")

    lines.append("## Per-task results")
    lines.append("")
    lines.append("| Model | Task | Trials | Passed | Pass rate | pass@k | pass^k | Mean score |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| `{row['Model']}` | {row['Task ID']} | {row['Trials']} | {row['Passed']} "
            f"| {row.get('Pass Rate (%)', 'n/a')}% | {row.get('pass@k', 'n/a')} | {row.get('pass^k', 'n/a')} "
            f"| {row.get('Mean Score (%)', 'n/a')}% |"
        )
    lines.append("")

    failures = defaultdict(int)
    for records in raw.values():
        for rec in records:
            for reason in rec.get("failure_reasons") or []:
                failures[str(reason)[:140]] += 1
    if failures:
        lines.append("## Observed failure modes")
        lines.append("")
        lines.append("| Count | Failure reason (as recorded by the grader) |")
        lines.append("|---|---|")
        for reason, count in sorted(failures.items(), key=lambda kv: -kv[1]):
            lines.append(f"| {count} | {reason} |")
        lines.append("")

    if adapter_errors:
        lines.append("## Adapter errors (harness/transport, not model reasoning)")
        lines.append("")
        for name, err in adapter_errors[:20]:
            lines.append(f"- `{name}`: {str(err)[:200]}")
        lines.append("")

    lines.append("## Reproduction")
    lines.append("")
    lines.append("```bash")
    lines.append("export MECHEVAL_BASE_URL=<openai-compatible base url>")
    lines.append("export MECHEVAL_API_KEY=<your key>")
    lines.append("python experiments/run_experiment.py --validate-models   # catalogue preflight")
    lines.append("python experiments/run_experiment.py --trials 3")
    lines.append("python reports/generate_report.py")
    lines.append("```")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    if not os.path.exists(SUMMARY):
        raise SystemExit(f"No results to report: {SUMMARY} is missing. Run the benchmark first.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    report = build_report()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"[+] Report written to {OUT} ({len(report)} chars)")
    print(f"    Source: {SUMMARY}")
    print(f"    Generated at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
