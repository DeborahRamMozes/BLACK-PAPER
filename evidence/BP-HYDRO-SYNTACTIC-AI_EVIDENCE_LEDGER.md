# Evidence Ledger

# BP-HYDRO-001: Hydro-Syntactic AI

**Date initiated:** 2026-06-20  
**Mode:** Evidence ledger  
**Purpose:** Track claims, evidence status, and research anchors for the Black Paper node.

---

## Core Claim Table

| ID | Claim | Evidence Status | Source Direction | Risk Level | Notes |
|---|---|---|---|---|---|
| C-001 | Water can be treated as a computational resource analogous to cache, storage, memory, energy, and thermal capacity. | Conceptual, needs technical formalization | Operating systems resource governance, cloud scheduling, datacenter sustainability metrics | Medium | Strong conceptual frame, needs engineering specification. |
| C-002 | Water Usage Effectiveness measures datacenter water use relative to electricity consumed. | Supported | Microsoft Datacenters definition of WUE | Low | Microsoft states WUE is measured in liters per kilowatt-hour. |
| C-003 | Datacenter water use depends on climate and location variables such as humidity and ambient temperature. | Supported | Microsoft Datacenters, ThirstyFLOPS | Low | Supports location-aware routing logic. |
| C-004 | HPC and AI workloads create both direct and indirect water footprints. | Supported | ThirstyFLOPS | Low | Direct water includes cooling. Indirect water includes electricity generation. |
| C-005 | Water-aware scheduling can be modeled alongside carbon-aware scheduling. | Supported | WaterWise, Wattnet, SCARF | Low to medium | The exact optimization tradeoff is context-dependent. |
| C-006 | A compiler or runtime guard can reduce water impact through caching, compression, model selection, rerouting, throttling, or refusal. | Plausible, needs prototype | Derived from cloud scheduling and resource quota logic | Medium | Needs implementation model and test environment. |
| C-007 | Sustainability reporting without enforcement does not guarantee resource reduction. | Analytical claim | Governance theory, audit systems, infrastructure policy | Medium | Requires careful framing to avoid overgeneralization. |

---

## Key Metrics

| Metric | Meaning | Use in Hydro-Syntactic AI |
|---|---|---|
| WUE | Water Usage Effectiveness, liters per kilowatt-hour | Estimate direct water cost of datacenter operation |
| PUE | Power Usage Effectiveness | Estimate facility energy overhead |
| EWF | Energy Water Factor | Estimate indirect water cost from electricity generation |
| Regional water stress | Local scarcity condition | Weight water impact by place and time |
| Token count | Approximate inference workload size | Estimate energy and downstream water cost |
| Model size | Compute intensity indicator | Select smallest sufficient model |
| Cache availability | Whether prior output can be reused | Avoid unnecessary generation |
| Latency tolerance | Whether a task can wait | Delay non-urgent workloads |

---

## Evidence Anchors

### 1. Microsoft Datacenters

Microsoft defines PUE and WUE as key metrics for datacenter efficiency. It defines WUE as water used relative to electricity consumed, measured in liters per kilowatt-hour. It also states that WUE is calculated using annual liters of water used for humidification and cooling divided by annual kWh used to power IT equipment.

Source: https://datacenters.microsoft.com/sustainability/efficiency/

### 2. ThirstyFLOPS

ThirstyFLOPS provides a water footprint modeling framework for high-performance computing. It uses WUE, PUE, and Energy Water Factor, and separates direct water footprint from indirect water footprint.

Source: https://arxiv.org/abs/2510.00471

### 3. WaterWise

WaterWise proposes job scheduling for geographically distributed data centers that co-optimizes carbon and water footprints.

Source: https://arxiv.org/abs/2501.17944

### 4. SCARF

SCARF argues that water consumption impact should be weighted by local and temporal water stress rather than treated as equal everywhere.

Source: https://arxiv.org/abs/2506.22773

### 5. Wattnet

Wattnet models electricity consumption with both carbon and water footprint analysis, using temporal and regional electricity flow tracing.

Source: https://arxiv.org/abs/2601.11623

---

## Prototype Requirements

A future prototype must test whether an AI middleware layer can evaluate resource cost before execution.

Minimum test fields:

```text
request_id
model_id
token_estimate
cache_hit
energy_estimate_kWh
WUE
PUE
EWF
regional_water_stress
water_budget_remaining
latency_tolerance
execution_decision
```

Minimum decisions:

```text
execute
use_cache
compress_output
use_smaller_model
delay
reroute
throttle
refuse
```

---

## Public Safety Note

This ledger is a public-facing research artifact. It does not include private operational codes, hidden watermark systems, or unpublished internal protocols.
