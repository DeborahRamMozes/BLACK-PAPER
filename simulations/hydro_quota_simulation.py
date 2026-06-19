#!/usr/bin/env python3
"""
BP-HYDRO-001 synthetic simulation.

Purpose:
Compare ordinary AI execution against a Hydro-Quota Protocol that treats
water as a runtime quota.

Important:
This is a synthetic simulation. It does not measure any real provider,
real data center, or real model. Values are invented but structurally
plausible for demonstrating governance behavior.

Run:
python simulations/hydro_quota_simulation.py
"""

from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Dict, List


SEED = 1976
JOBS = 1000


@dataclass
class DataCenter:
    key: str
    name: str
    WUE: float
    PUE: float
    EWF: float
    stress: float


DATA_CENTERS: Dict[str, DataCenter] = {
    "DC_A": DataCenter("DC_A", "HighWUE_HighStress", WUE=1.80, PUE=1.28, EWF=1.00, stress=0.85),
    "DC_B": DataCenter("DC_B", "LowWUE_LowStress", WUE=0.35, PUE=1.15, EWF=0.55, stress=0.20),
    "DC_C": DataCenter("DC_C", "MediumWUE_MedStress", WUE=0.90, PUE=1.22, EWF=0.75, stress=0.50),
}

TASK_TYPES = [
    ("simple_qa", 0.30, 250, 350, "medium", ["low", "medium"]),
    ("essay_draft", 0.22, 900, 1800, "large", ["medium", "low"]),
    ("code_help", 0.18, 700, 1200, "large", ["medium", "high"]),
    ("summary", 0.15, 1500, 700, "medium", ["low", "medium"]),
    ("repetitive_variants", 0.10, 500, 5000, "large", ["low"]),
    ("critical_support", 0.05, 600, 1000, "large", ["high"]),
]

MODEL_ENERGY_PER_1K_TOKENS = {
    "small": 0.0008,
    "medium": 0.0022,
    "large": 0.0060,
}

MODEL_QUALITY_CAPACITY = {"small": 1, "medium": 2, "large": 3}
TASK_REQUIRED_CAPACITY = {
    "simple_qa": 1,
    "essay_draft": 2,
    "code_help": 2,
    "summary": 1,
    "repetitive_variants": 1,
    "critical_support": 3,
}


def choose_task_type() -> tuple:
    r = random.random()
    cumulative = 0.0
    for task in TASK_TYPES:
        cumulative += task[1]
        if r <= cumulative:
            return task
    return TASK_TYPES[-1]


def jitter_tokens(mean: int) -> int:
    value = random.gauss(mean, mean * 0.25)
    return max(50, int(value))


def energy_kwh(tokens: int, model: str) -> float:
    return (tokens / 1000.0) * MODEL_ENERGY_PER_1K_TOKENS[model]


def water_liters(kwh: float, dc: DataCenter) -> float:
    return kwh * (dc.WUE + dc.PUE * dc.EWF)


def minimum_model_for_task(task: str) -> str:
    required = TASK_REQUIRED_CAPACITY[task]
    for model in ["small", "medium", "large"]:
        if MODEL_QUALITY_CAPACITY[model] >= required:
            return model
    return "large"


def build_workload() -> List[dict]:
    random.seed(SEED)
    workload = []

    for job_id in range(1, JOBS + 1):
        task, _, mean_in, mean_out, requested_model, urgency_options = choose_task_type()
        urgency = random.choice(urgency_options)
        input_tokens = jitter_tokens(mean_in)
        output_tokens = jitter_tokens(mean_out)
        cache_possible = task in ["simple_qa", "summary"] and random.random() < (
            0.28 if task == "simple_qa" else 0.18
        )

        workload.append(
            {
                "id": job_id,
                "task": task,
                "urgency": urgency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "requested_model": requested_model,
                "cache_possible": cache_possible,
            }
        )

    return workload


def run_baseline(workload: List[dict]) -> List[dict]:
    rows = []
    dc = DATA_CENTERS["DC_A"]

    for job in workload:
        tokens = job["input_tokens"] + job["output_tokens"]
        model = job["requested_model"]
        kwh = energy_kwh(tokens, model)
        water = water_liters(kwh, dc)

        rows.append(
            {
                **job,
                "decision": "execute",
                "model": model,
                "dc": dc.key,
                "tokens_run": tokens,
                "energy_kWh": kwh,
                "water_L": water,
                "stress_weighted_water_L": water * (1 + dc.stress),
            }
        )

    return rows


def run_hydro_quota(workload: List[dict], hourly_budget_liters: float = 0.55) -> List[dict]:
    rows = []
    used_liters = 0.0

    for job in workload:
        decision = []
        original_tokens = job["input_tokens"] + job["output_tokens"]
        task = job["task"]
        urgency = job["urgency"]

        if job["cache_possible"]:
            model = "small"
            dc = DATA_CENTERS["DC_B"]
            tokens_run = max(25, int(original_tokens * 0.03))
            decision.append("use_cache")
        else:
            model = minimum_model_for_task(task)
            dc = DATA_CENTERS["DC_B"]
            tokens_run = original_tokens

            if task == "repetitive_variants":
                tokens_run = job["input_tokens"] + min(job["output_tokens"], 1200)
                decision.append("compress_output")
            elif task == "essay_draft" and urgency == "low":
                tokens_run = job["input_tokens"] + int(job["output_tokens"] * 0.65)
                decision.append("compress_output")
            elif task == "summary":
                tokens_run = job["input_tokens"] + int(job["output_tokens"] * 0.75)
                decision.append("compress_output")

            if model != job["requested_model"]:
                decision.append("use_smaller_model")

        kwh = energy_kwh(tokens_run, model)
        water = water_liters(kwh, dc)

        if used_liters + water > hourly_budget_liters:
            if urgency == "high":
                decision.append("execute_emergency_over_budget")
                used_liters += water
            elif urgency == "medium":
                decision.append("delay")
                tokens_run = 0
                kwh = 0.000005
                water = 0.00001
            else:
                decision.append("refuse_or_batch_later")
                tokens_run = 0
                kwh = 0.000002
                water = 0.000005
        else:
            used_liters += water

        rows.append(
            {
                **job,
                "decision": "+".join(decision) if decision else "execute",
                "model": model,
                "dc": dc.key,
                "tokens_run": tokens_run,
                "energy_kWh": kwh,
                "water_L": water,
                "stress_weighted_water_L": water * (1 + dc.stress),
            }
        )

    return rows


def total(rows: List[dict], key: str) -> float:
    return sum(float(row[key]) for row in rows)


def count_by(rows: List[dict], key: str) -> dict:
    return dict(Counter(row[key] for row in rows))


def summarize_by_task(baseline: List[dict], hydro: List[dict]) -> List[dict]:
    tasks = sorted({row["task"] for row in baseline})
    output = []

    for task in tasks:
        b_rows = [row for row in baseline if row["task"] == task]
        h_rows = [row for row in hydro if row["task"] == task]
        b_water = total(b_rows, "water_L")
        h_water = total(h_rows, "water_L")
        reduction = ((b_water - h_water) / b_water * 100) if b_water else 0.0

        output.append(
            {
                "task": task,
                "jobs": len(h_rows),
                "baseline_water_L": b_water,
                "hydro_water_L": h_water,
                "reduction_pct": reduction,
            }
        )

    return sorted(output, key=lambda row: row["baseline_water_L"], reverse=True)


def main() -> None:
    workload = build_workload()
    baseline = run_baseline(workload)
    hydro = run_hydro_quota(workload)

    summary = {
        "total_jobs": JOBS,
        "baseline_energy_kWh": total(baseline, "energy_kWh"),
        "hydro_energy_kWh": total(hydro, "energy_kWh"),
        "baseline_water_L": total(baseline, "water_L"),
        "hydro_water_L": total(hydro, "water_L"),
        "baseline_stress_weighted_water_L": total(baseline, "stress_weighted_water_L"),
        "hydro_stress_weighted_water_L": total(hydro, "stress_weighted_water_L"),
        "baseline_tokens_run": int(total(baseline, "tokens_run")),
        "hydro_tokens_run": int(total(hydro, "tokens_run")),
        "decision_counts": count_by(hydro, "decision"),
        "baseline_model_counts": count_by(baseline, "model"),
        "hydro_model_counts": count_by(hydro, "model"),
        "task_summary": summarize_by_task(baseline, hydro),
        "data_centers": {key: asdict(dc) for key, dc in DATA_CENTERS.items()},
    }

    summary["energy_reduction_pct"] = (
        (summary["baseline_energy_kWh"] - summary["hydro_energy_kWh"])
        / summary["baseline_energy_kWh"]
        * 100
    )
    summary["water_reduction_pct"] = (
        (summary["baseline_water_L"] - summary["hydro_water_L"])
        / summary["baseline_water_L"]
        * 100
    )
    summary["stress_weighted_water_reduction_pct"] = (
        (
            summary["baseline_stress_weighted_water_L"]
            - summary["hydro_stress_weighted_water_L"]
        )
        / summary["baseline_stress_weighted_water_L"]
        * 100
    )
    summary["tokens_run_reduction_pct"] = (
        (summary["baseline_tokens_run"] - summary["hydro_tokens_run"])
        / summary["baseline_tokens_run"]
        * 100
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
