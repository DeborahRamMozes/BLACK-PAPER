# BP-HYDRO-001 Formula: Hydro-Quota vs Gemini Baseline

**Date:** 2026-06-20  
**Node:** BP-HYDRO-001 / Hydro-Syntactic AI  
**Purpose:** define the formula showing how Hydro-Quota can reduce estimated water below the published Gemini median text-prompt number.

---

## 1. Published Baseline

Google's 2025 Gemini serving paper reports a median Gemini Apps text prompt at:

```text
E_gemini = 0.24 Wh per median text prompt
W_gemini = 0.26 mL water per median text prompt
```

This file treats that as the direct prompt-water baseline.

---

## 2. Hydro-Quota Policy Multiplier

Hydro-Quota reduces execution through five controls:

| Control | Share of jobs | Energy multiplier |
|---|---:|---:|
| Cache hit | 30% | 0.10 |
| Smaller sufficient model | 35% | 0.50 |
| Compressed output | 20% | 0.70 |
| Delayed / batched work | 10% | 0.20 |
| Full priority execution | 5% | 1.00 |

Formula:

```text
M_hydro = (0.30 * 0.10)
        + (0.35 * 0.50)
        + (0.20 * 0.70)
        + (0.10 * 0.20)
        + (0.05 * 1.00)

M_hydro = 0.415
```

Meaning:

```text
Hydro-Quota runs at 41.5% of Gemini baseline execution energy under this scenario.
```

---

## 3. Level 1 Formula: Gemini-only Water Reduction

This version uses Google's own reported water baseline and applies only the Hydro-Quota execution multiplier.

```text
W_hydro_level_1 = W_gemini * M_hydro
```

Substitution:

```text
W_hydro_level_1 = 0.26 mL * 0.415
W_hydro_level_1 = 0.1079 mL per prompt-equivalent job
```

Savings:

```text
Saved_level_1 = W_gemini - W_hydro_level_1
Saved_level_1 = 0.26 - 0.1079
Saved_level_1 = 0.1521 mL per job
```

Reduction:

```text
Reduction_level_1 = Saved_level_1 / W_gemini
Reduction_level_1 = 0.1521 / 0.26
Reduction_level_1 = 58.5%
```

### Level 1 Result

```text
Gemini baseline: 0.26 mL/job
Hydro-Quota Level 1: 0.1079 mL/job
Saving: 58.5%
```

This already shows Hydro-Quota below the Gemini baseline.

---

## 4. Level 2 Formula: Hydro Policy + Low-WUE Routing

This version uses Gemini's published energy per prompt and applies Hydro-Quota execution reduction plus low-WUE routing.

Published / scenario values:

```text
E_gemini = 0.24 Wh = 0.00024 kWh
M_hydro = 0.415
WUE_low = 0.12 L/kWh
```

Formula:

```text
E_hydro = E_gemini * M_hydro
W_hydro_level_2_L = E_hydro * WUE_low
W_hydro_level_2_mL = W_hydro_level_2_L * 1000
```

Substitution:

```text
E_hydro = 0.00024 kWh * 0.415
E_hydro = 0.0000996 kWh

W_hydro_level_2_L = 0.0000996 * 0.12
W_hydro_level_2_L = 0.000011952 L

W_hydro_level_2_mL = 0.000011952 * 1000
W_hydro_level_2_mL = 0.011952 mL per job
```

Savings:

```text
Saved_level_2 = W_gemini - W_hydro_level_2_mL
Saved_level_2 = 0.26 - 0.011952
Saved_level_2 = 0.248048 mL per job
```

Reduction:

```text
Reduction_level_2 = Saved_level_2 / W_gemini
Reduction_level_2 = 0.248048 / 0.26
Reduction_level_2 = 95.40%
```

### Level 2 Result

```text
Gemini baseline: 0.26 mL/job
Hydro-Quota Level 2: 0.011952 mL/job
Saving: 95.40%
```

This shows Hydro-Quota below Gemini baseline with both execution control and low-WUE routing.

---

## 5. Scale Table

| Jobs | Gemini baseline water mL | Hydro Level 1 mL | Level 1 saved mL | Hydro Level 2 mL | Level 2 saved mL |
|---:|---:|---:|---:|---:|---:|
| 100 | 26.00 | 10.79 | 15.21 | 1.20 | 24.80 |
| 500 | 130.00 | 53.95 | 76.05 | 5.98 | 124.02 |
| 1,000 | 260.00 | 107.90 | 152.10 | 11.95 | 248.05 |
| 2,500 | 650.00 | 269.75 | 380.25 | 29.88 | 620.12 |
| 5,000 | 1,300.00 | 539.50 | 760.50 | 59.76 | 1,240.24 |

---

## 6. Daily, Monthly, Yearly Level 2 Savings

Assumption: job count means jobs per day.

| Jobs per day | Gemini baseline L/day | Hydro Level 2 L/day | Saved L/day | Saved L/30-day month | Saved L/year |
|---:|---:|---:|---:|---:|---:|
| 100 | 0.0260 | 0.0012 | 0.0248 | 0.74 | 9.05 |
| 500 | 0.1300 | 0.0060 | 0.1240 | 3.72 | 45.27 |
| 1,000 | 0.2600 | 0.0120 | 0.2481 | 7.44 | 90.54 |
| 2,500 | 0.6500 | 0.0299 | 0.6201 | 18.60 | 226.34 |
| 5,000 | 1.3000 | 0.0598 | 1.2402 | 37.21 | 452.69 |

---

## 7. Claim Boundary

The correct claim is:

```text
Using Google's published median prompt water value as baseline,
Hydro-Quota Level 1 reduces estimated per-job water from 0.26 mL to 0.1079 mL.

Using Gemini energy plus low-WUE routing,
Hydro-Quota Level 2 reduces estimated per-job water from 0.26 mL to 0.011952 mL.
```

Do not claim this proves real-world provider savings yet.

Claim this:

```text
The formula shows that a water-aware runtime policy can be modeled below the published Gemini median prompt baseline.
The next step is production telemetry.
```
