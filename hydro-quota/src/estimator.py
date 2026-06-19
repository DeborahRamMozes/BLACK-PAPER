"""Water and energy estimator for Hydro-Quota."""

from __future__ import annotations

from dataclasses import dataclass, asdict


MODEL_ENERGY_KWH_PER_TOKEN = {
    "small": 0.0000000008,
    "medium": 0.0000000022,
    "large": 0.0000000060,
}


@dataclass
class Estimate:
    energy_kWh: float
    direct_water_L: float
    indirect_water_L: float
    total_water_L: float
    stress_weighted_water_L: float

    def to_dict(self) -> dict:
        return asdict(self)


def estimate_energy_kwh(tokens: int, model: str) -> float:
    if model not in MODEL_ENERGY_KWH_PER_TOKEN:
        raise ValueError(f"Unknown model size: {model}")
    return max(tokens, 0) * MODEL_ENERGY_KWH_PER_TOKEN[model]


def estimate_water(
    tokens: int,
    model: str,
    WUE_L_per_kWh: float,
    PUE: float,
    EWF_L_per_kWh: float,
    water_stress_index: float,
) -> Estimate:
    energy = estimate_energy_kwh(tokens, model)
    direct = energy * WUE_L_per_kWh
    indirect = energy * PUE * EWF_L_per_kWh
    total = direct + indirect
    stress_weighted = total * (1 + water_stress_index)

    return Estimate(
        energy_kWh=energy,
        direct_water_L=direct,
        indirect_water_L=indirect,
        total_water_L=total,
        stress_weighted_water_L=stress_weighted,
    )
