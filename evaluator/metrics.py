"""
MechEval Benchmark Metrics Calculator.
Computes pass@k, pass^k, mean score, latency, cost, and failure mode distribution.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from evaluator.runner import TrialRecord


class BenchmarkMetrics:
    @staticmethod
    def compute_summary(records: List[TrialRecord]) -> Dict[str, Any]:
        """
        Computes comprehensive evaluation metrics from trial records.
        """
        if not records:
            return {}

        df = pd.DataFrame([r.model_dump() for r in records])

        model_name = records[0].model_name
        total_trials = len(records)
        unique_tasks = df["task_id"].unique()
        num_tasks = len(unique_tasks)

        task_metrics = []

        for task_id in unique_tasks:
            task_df = df[df["task_id"] == task_id]
            k = len(task_df)
            passes = task_df["all_passed"].sum()
            avg_score = task_df["score"].mean()
            parse_success_rate = task_df["parse_success"].mean()

            # pass@k: at least 1 pass in k trials
            pass_at_k = 1.0 if passes >= 1 else 0.0
            # pass^k: passed ALL k trials
            pass_pow_k = 1.0 if passes == k else 0.0

            # Gather observed failures for this task
            failures = []
            for _, row in task_df.iterrows():
                for fail in row["failure_reasons"]:
                    failures.append(fail)

            task_metrics.append({
                "task_id": task_id,
                "task_title": task_df["task_title"].iloc[0],
                "trials_run": k,
                "passed_trials": int(passes),
                "pass_rate": passes / k if k > 0 else 0.0,
                "pass@k": pass_at_k,
                "pass^k": pass_pow_k,
                "avg_score": avg_score,
                "parse_success_rate": parse_success_rate,
                "avg_latency_s": task_df["latency_seconds"].mean(),
                "common_failures": failures[:3],
            })

        task_summary_df = pd.DataFrame(task_metrics)

        # Aggregate metrics across entire benchmark
        overall_pass_at_k = task_summary_df["pass@k"].mean()
        overall_pass_pow_k = task_summary_df["pass^k"].mean()
        overall_mean_score = df["score"].mean()
        overall_pass_rate = df["all_passed"].mean()
        total_cost_usd = df["estimated_cost_usd"].sum()
        total_runtime_s = df["latency_seconds"].sum()

        summary = {
            "model_name": model_name,
            "total_trials": total_trials,
            "total_tasks": num_tasks,
            "overall_pass_rate": overall_pass_rate,
            "overall_pass@k": overall_pass_at_k,
            "overall_pass^k": overall_pass_pow_k,
            "overall_mean_score": overall_mean_score,
            "total_cost_usd": total_cost_usd,
            "total_runtime_s": total_runtime_s,
            "task_breakdown": task_metrics,
        }

        return summary

    @staticmethod
    def to_dataframe(task_breakdown: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts task breakdown to tabular DataFrame for CSV/reporting."""
        rows = []
        for t in task_breakdown:
            rows.append({
                "Task ID": t["task_id"],
                "Task Title": t["task_title"],
                "Trials": t["trials_run"],
                "Passed": t["passed_trials"],
                "Pass Rate (%)": round(t["pass_rate"] * 100.0, 1),
                "pass@k": t["pass@k"],
                "pass^k": t["pass^k"],
                "Mean Score (%)": round(t["avg_score"] * 100.0, 1),
                "Avg Latency (s)": round(t["avg_latency_s"], 2),
            })
        return pd.DataFrame(rows)
