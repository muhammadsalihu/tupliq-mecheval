# MechEval Benchmark Report

Generated from live trials by `python reports/generate_report.py`. Every figure in this report is read from `results/summary.csv`, `results/raw/*.json` and `results/run_environment.json`.

## Run environment

- **Endpoint**: `https://inference-api.nousresearch.com/v1`
- **Models**: `openai/gpt-6-luna`, `deepseek/deepseek-v4.1-flash`, `z-ai/glm-5.3-flash`, `anthropic/claude-haiku-5.5`
- **Trials per task**: 3
- **Trials recorded**: 60
- **Recorded spend** (sum of per-call `estimated_cost_usd`): $0.1174
- **Latency**: mean 46.6s, min 3.4s, max 420.1s
- **Run completed**: 2026-11-09T04:43:54.662615+00:00

## Headline results

Aggregated from the trial records in `results/raw/` — pass rate = trials passed / trials run; pass@k = share of tasks with at least one passing trial; pass^k = share of tasks where every trial passed.

| Model | Trials | Passed | Pass rate | pass@k | pass^k | Mean score | Mean latency (s) | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| `anthropic/claude-haiku-5.5` | 15 | 9 | 60.0% | 60.0% | 60.0% | 82.1% | 8.3 | $0.0146 |
| `deepseek/deepseek-v4.1-flash` | 15 | 9 | 60.0% | 60.0% | 60.0% | 82.1% | 67.4 | $0.0563 |
| `openai/gpt-6-luna` | 15 | 9 | 60.0% | 60.0% | 60.0% | 80.7% | 9.2 | $0.0073 |
| `z-ai/glm-5.3-flash` | 15 | 5 | 33.3% | 40.0% | 20.0% | 66.3% | 101.3 | $0.0393 |

## Per-task results

| Model | Task | Trials | Passed | Pass rate | pass@k | pass^k | Mean score |
|---|---|---|---|---|---|---|---|
| `openai/gpt-6-luna` | task_001_cantilever | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `openai/gpt-6-luna` | task_002_axial | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `openai/gpt-6-luna` | task_003_boundary | 3 | 0 | 0.0% | 0.0 | 0.0 | 83.3% |
| `openai/gpt-6-luna` | task_004_thermal | 3 | 0 | 0.0% | 0.0 | 0.0 | 20.3% |
| `openai/gpt-6-luna` | task_005_convergence | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | task_001_cantilever | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | task_002_axial | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `deepseek/deepseek-v4.1-flash` | task_003_boundary | 3 | 0 | 0.0% | 0.0 | 0.0 | 90.0% |
| `deepseek/deepseek-v4.1-flash` | task_004_thermal | 3 | 0 | 0.0% | 0.0 | 0.0 | 20.3% |
| `deepseek/deepseek-v4.1-flash` | task_005_convergence | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `z-ai/glm-5.3-flash` | task_001_cantilever | 3 | 2 | 66.7% | 1.0 | 0.0 | 93.8% |
| `z-ai/glm-5.3-flash` | task_002_axial | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `z-ai/glm-5.3-flash` | task_003_boundary | 3 | 0 | 0.0% | 0.0 | 0.0 | 90.0% |
| `z-ai/glm-5.3-flash` | task_004_thermal | 3 | 0 | 0.0% | 0.0 | 0.0 | 20.3% |
| `z-ai/glm-5.3-flash` | task_005_convergence | 3 | 0 | 0.0% | 0.0 | 0.0 | 27.5% |
| `anthropic/claude-haiku-5.5` | task_001_cantilever | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `anthropic/claude-haiku-5.5` | task_002_axial | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |
| `anthropic/claude-haiku-5.5` | task_003_boundary | 3 | 0 | 0.0% | 0.0 | 0.0 | 90.0% |
| `anthropic/claude-haiku-5.5` | task_004_thermal | 3 | 0 | 0.0% | 0.0 | 0.0 | 20.3% |
| `anthropic/claude-haiku-5.5` | task_005_convergence | 3 | 3 | 100.0% | 1.0 | 1.0 | 100.0% |

## Observed failure modes

| Count | Failure reason (as recorded by the grader) |
|---|---|
| 12 | free_thermal_expansion_mm: candidate=2.295 mm, reference=2.3354999999999997 mm (Exceeds tolerance (rel_error: 1.7341%, allowed: 1.00%)) |
| 12 | restrained_expansion_mm: candidate=1.095 mm, reference=1.1355 mm (Exceeds tolerance (rel_error: 3.5667%, allowed: 1.00%)) |
| 11 | thermal_stress_MPa: candidate=140.89 MPa, reference=146.101 MPa (Exceeds tolerance (rel_error: 3.5667%, allowed: 1.00%)) |
| 11 | reaction_force_N: candidate=225424.0 N, reference=233761.6 N (Exceeds tolerance (rel_error: 3.5667%, allowed: 1.00%)) |
| 4 | temperature_to_close_gap_C: candidate=67.0588 deg C, reference=66.24277456647398 deg C (Exceeds tolerance (rel_error: 1.2319%, allowed: 1.00 |
| 4 | max_deflection_mm: candidate=1.2174 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 19.0361%, allowed: 1.00%)) |
| 3 | temperature_to_close_gap_C: candidate=67.05882352941177 deg C, reference=66.24277456647398 deg C (Exceeds tolerance (rel_error: 1.2319%, all |
| 2 | max_deflection_mm: candidate=1.217438456568721 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 19.0398%, allowed: 1.00%)) |
| 2 | max_deflection_mm: candidate=1.217438 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 19.0398%, allowed: 1.00%)) |
| 2 | temperature_to_close_gap_C: candidate=67.0588235294 deg C, reference=66.24277456647398 deg C (Exceeds tolerance (rel_error: 1.2319%, allowed |
| 2 | Model adapter execution error: Exception during API call: HTTPSConnectionPool(host='inference-api.nousresearch.com', port=443): Read timed o |
| 1 | max_deflection_mm: candidate=1.217 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 18.9970%, allowed: 1.00%)) |
| 1 | max_deflection_mm: candidate=1.22 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 19.2903%, allowed: 1.00%)) |
| 1 | max_deflection_mm: candidate=1.218 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 19.0947%, allowed: 1.00%)) |
| 1 | temperature_to_close_gap_C: candidate=67.06 deg C, reference=66.24277456647398 deg C (Exceeds tolerance (rel_error: 1.2337%, allowed: 1.00%) |
| 1 | max_deflection_mm: candidate=1.2174384565687184 mm, reference=1.0227152639581227 mm (Exceeds tolerance (rel_error: 19.0398%, allowed: 1.00%) |
| 1 | max_positive_moment_Nm: candidate=1500.0 N*m, reference=13500.0 N*m (Exceeds tolerance (rel_error: 88.8889%, allowed: 1.00%)) |
| 1 | max_positive_moment_Nm: candidate=15000.0 N*m, reference=13500.0 N*m (Exceeds tolerance (rel_error: 11.1111%, allowed: 1.00%)) |
| 1 | temperature_to_close_gap_C: candidate=67.0588235 deg C, reference=66.24277456647398 deg C (Exceeds tolerance (rel_error: 1.2319%, allowed: 1 |
| 1 | thermal_stress_MPa: candidate=140.79 MPa, reference=146.101 MPa (Exceeds tolerance (rel_error: 3.6352%, allowed: 1.00%)) |
| 1 | reaction_force_N: candidate=225264.0 N, reference=233761.6 N (Exceeds tolerance (rel_error: 3.6352%, allowed: 1.00%)) |
| 1 | tip_deflection_mm: candidate=20.6480902778 mm, reference=20.150736742058903 mm (Exceeds tolerance (rel_error: 2.4682%, allowed: 1.00%)) |
| 1 | temperature_to_close_gap_C: candidate=67.05882352941175 deg C, reference=66.24277456647398 deg C (Exceeds tolerance (rel_error: 1.2319%, all |
| 1 | fine_mesh_discretization_error_percent: candidate=1.796407 %, reference=0.5952380952381001 % (Exceeds tolerance (rel_error: 201.7964%, allow |

## Adapter errors (harness/transport, not model reasoning)

- `z-ai-glm-5.3-flash`: Exception during API call: HTTPSConnectionPool(host='inference-api.nousresearch.com', port=443): Read timed out. (read timeout=420)
- `z-ai-glm-5.3-flash`: Exception during API call: HTTPSConnectionPool(host='inference-api.nousresearch.com', port=443): Read timed out. (read timeout=420)

## Reproduction

```bash
export MECHEVAL_BASE_URL=<openai-compatible base url>
export MECHEVAL_API_KEY=<your key>
python experiments/run_experiment.py --validate-models   # catalogue preflight
python experiments/run_experiment.py --trials 3
python reports/generate_report.py
```

