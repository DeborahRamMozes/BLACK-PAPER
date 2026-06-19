# Hydro-Quota Prototype

First runnable prototype for BP-HYDRO-001 / Hydro-Syntactic AI.

This prototype turns the Black Paper claim into a simple command-line system:

```text
Water becomes measurable.
Water becomes quota.
Quota changes execution.
Execution becomes auditable.
```

## Purpose

Hydro-Quota estimates energy and water cost before execution and returns an execution decision:

```text
execute_full
use_cache
use_smaller_model
compress_output
delay_or_batch
reroute_low_water
refuse
emergency_override
```

This is not connected to a real AI provider yet. It is a prototype skeleton using explicit assumptions.

## Run Example

```bash
python src/main.py --task essay --urgency low --input-tokens 900 --output-tokens 3000 --model large --cache-allowed
```

## Folder Structure

```text
hydro-quota/
├── README.md
├── config/
│   └── sample_regions.json
├── src/
│   ├── estimator.py
│   ├── quota_engine.py
│   └── main.py
└── tests/
    └── test_quota_engine.py
```

## Note

This is public-facing research code. It uses scenario values and transparent assumptions, not live provider telemetry.
