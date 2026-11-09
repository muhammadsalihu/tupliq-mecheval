"""
MechEval Task Runner & Execution Harness.
Orchestrates multi-trial evaluations, manages clean trial environments,
collects transcripts, runs deterministic graders, and logs structured outputs.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from tasks.base import BaseTask
from graders.simulation_grader import GradingReport
from evaluator.model_adapter import BaseModelAdapter, ModelResponse


def _slug_for_path(model_name: str) -> str:
    """Model ids are provider-prefixed ('openai/gpt-6-luna'): a '/' would nest a path, so flatten it."""
    return (model_name or "model").replace("/", "-")


class TrialRecord(BaseModel):
    task_id: str
    task_title: str
    model_name: str
    trial_index: int
    timestamp: float
    prompt: str
    raw_response: str
    parsed_json: Optional[Dict[str, Any]] = None
    parse_success: bool = False
    latency_seconds: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    adapter_error: Optional[str] = None
    all_passed: bool = False
    score: float = 0.0
    failure_reasons: List[str] = []
    parameter_results: List[Dict[str, Any]] = []


class BenchmarkRunner:
    def __init__(
        self,
        tasks: List[BaseTask],
        adapter: BaseModelAdapter,
        num_trials: int = 3,
        transcripts_dir: str = "transcripts",
        results_dir: str = "results/raw",
    ):
        self.tasks = tasks
        self.adapter = adapter
        self.num_trials = num_trials
        self.transcripts_dir = transcripts_dir
        self.results_dir = results_dir

        os.makedirs(transcripts_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)

    def run_trial(self, task: BaseTask, trial_index: int) -> TrialRecord:
        """Executes a single trial for a task with clean transcript logging."""
        prompt = task.get_prompt()
        timestamp = time.time()

        # Generate response from model
        resp = self.adapter.generate(prompt=prompt)

        # Grade candidate
        all_passed = False
        score = 0.0
        failure_reasons = []
        param_results = []

        if resp.error:
            failure_reasons.append(f"Model adapter execution error: {resp.error}")
        elif not resp.parse_success or not resp.parsed_json:
            failure_reasons.append("Failed to extract valid JSON engineering output from response.")
        else:
            try:
                grading_report: GradingReport = task.grade(resp.parsed_json)
                all_passed = grading_report.all_passed
                score = grading_report.score
                failure_reasons = grading_report.failure_reasons
                param_results = grading_report.parameter_results
            except Exception as e:
                failure_reasons.append(f"Grader execution exception: {str(e)}")

        record = TrialRecord(
            task_id=task.task_id,
            task_title=task.title,
            model_name=self.adapter.model_name,
            trial_index=trial_index,
            timestamp=timestamp,
            prompt=prompt,
            raw_response=resp.raw_text,
            parsed_json=resp.parsed_json,
            parse_success=resp.parse_success,
            latency_seconds=resp.latency_seconds,
            prompt_tokens=resp.prompt_tokens,
            completion_tokens=resp.completion_tokens,
            estimated_cost_usd=resp.estimated_cost_usd,
            adapter_error=resp.error,
            all_passed=all_passed,
            score=score,
            failure_reasons=failure_reasons,
            parameter_results=param_results,
        )

        # Save formatted transcript
        transcript_filename = f"{_slug_for_path(self.adapter.model_name)}_{task.task_id}_trial_{trial_index + 1}.md"
        transcript_path = os.path.join(self.transcripts_dir, transcript_filename)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(f"# MechEval Transcript\n")
            f.write(f"- **Task**: {task.task_id} ({task.title})\n")
            f.write(f"- **Model**: {self.adapter.model_name}\n")
            f.write(f"- **Trial**: {trial_index + 1} of {self.num_trials}\n")
            f.write(f"- **Passed**: {all_passed}\n")
            f.write(f"- **Score**: {score:.2%}\n")
            f.write(f"- **Latency**: {resp.latency_seconds:.2f}s\n\n")
            f.write(f"## System Prompt / Instructions\n```\n{prompt}\n```\n\n")
            f.write(f"## Model Response\n{resp.raw_text}\n\n")
            f.write(f"## Grader Outcome\n")
            if all_passed:
                f.write(f"**ALL CHECKS PASSED (100% accurate)**\n")
            else:
                f.write(f"**FAILED CHECKS:**\n")
                for reason in failure_reasons:
                    f.write(f"- {reason}\n")

        return record

    def run_benchmark(self) -> List[TrialRecord]:
        """Runs full benchmark suite across all tasks and trials."""
        all_records = []
        for task in self.tasks:
            for trial_idx in range(self.num_trials):
                record = self.run_trial(task, trial_idx)
                all_records.append(record)

        # Save raw JSON results
        output_file = os.path.join(self.results_dir, f"{_slug_for_path(self.adapter.model_name)}_raw_results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in all_records], f, indent=2)

        return all_records
