#!/usr/bin/env python3
"""
BP-HYDRO-001 real-data-anchored Hydro-Quota simulation.

This script compares baseline text-prompt execution against a Hydro-Quota
policy for job counts from 100 to 5000.

Published anchors used:
1. Google 2025 Gemini serving paper: median Gemini Apps text prompt consumes
   0.24 Wh electricity and 0.26 mL water under Google's accounting framework.
2. Amazon 2026 sustainability disclosure: AWS global data center operations
   used 0.12 L/kWh WUE in 2025.

This is not provider telemetry. It is a reproducible scenario model using
published public values plus explicit policy assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


JOB_COUNTS = [100, 500, 1000, 2500, 5000]

# Published values.
GOOGLE_MEDIAN_PROMPT_ENERGY_WH = 0.24
GOOGLE_MEDIAN_PROMPT_WATER_ML = 0.26
AWS_WUE_L_PER_KWH = 0.12

# Hydro-Quota policy assumptions.
# The tuple is: share of workload, energy multiplier relative to baseline prompt.
HYDRO_POLICY: Dict[str, tuple[float, float]] = {
    "cache_hit": (0.30, 0.10),
    "small_model": (0.35, 0.50),
    "compress_output": (0.20, 0.70),
    "delay_or_batch": (0.10, 0.20),
    "full_priority": (0.05, 1.00),
}


@dataclass
class Row:
    jobs: int
    baseline_energy_Wh: float
    baseline_direct_water_mL: float
    hydro_energy_Wh: float
    hydro_direct_water_mL: float
    direct_water_saved_mL: float
    water_reduction_pct: float
    energy_reduction_pct: float


def hydro_energy_multiplier() -> float:
    return sum(share * multiplier for share, multiplier in HYDRO_POLICY.values())


def hydro_water_ml(energy_wh: float) -> float:
    kwh = energy_wh / 1000.0
    liters = kwh * AWS_WUE_L_PER_KWH
    return liters * 1000.0


def simulate() -> List[Row]:
    rows: List[Row] = []
    multiplier = hydro_energy_multiplier()

    for jobs in JOB_COUNTS:
        baseline_energy = jobs * GOOGLE_MEDIAN_PROMPT_ENERGY_WH
        baseline_water = jobs * GOOGLE_MEDIAN_PROMPT_WATER_ML
        hydro_energy = baseline_energy * multiplier
        hydro_water = hydro_water_ml(hydro_energy)
        water_saved = baseline_water - hydro_water
        water_reduction = (water_saved / baseline_water) * 100.0
        energy_reduction = ((baseline_energy - hydro_energy) / baseline_energy) * 100.0

        rows.append(
            Row(
                jobs=jobs,
                baseline_energy_Wh=baseline_energy,
                baseline_direct_water_mL=baseline_water,
                hydro_energy_Wh=hydro_energy,
                hydro_direct_water_mL=hydro_water,
                direct_water_saved_mL=water_saved,
                water_reduction_pct=water_reduction,
                energy_reduction_pct=energy_reduction,
            )
        )

    return rows


def print_markdown(rows: List[Row]) -> None:
    print("| Jobs | Baseline energy Wh | Baseline direct water mL | Hydro energy Wh | Hydro direct water mL | Water saved mL | Water reduction |")
    print("|---:|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row.jobs:,} | {row.baseline_energy_Wh:,.2f} | "
            f"{row.baseline_direct_water_mL:,.2f} | {row.hydro_energy_Wh:,.2f} | "
            f"{row.hydro_direct_water_mL:,.2f} | {row.direct_water_saved_mL:,.2f} | "
            f"{row.water_reduction_pct:.2f}% |"
        )

    print("\n| Jobs | Cache | Small model | Compress | Delay/batch | Full priority |")
    print("|---:|---:|---:|---:|---:|---:|")
    for jobs in JOB_COUNTS:
        counts = {key: int(jobs * share) for key, (share, _) in HYDRO_POLICY.items()}
        print(
            f"| {jobs:,} | {counts['cache_hit']:,} | {counts['small_model']:,} | "
            f"{counts['compress_output']:,} | {counts['delay_or_batch']:,} | "
            f"{counts['full_priority']:,} |"
        )


if __name__ == "__main__":
    print_markdown(simulate())
