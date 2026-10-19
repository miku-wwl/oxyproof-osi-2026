# Measured-only temperature decision analysis

Source: [Jang et al. dataset v1](https://doi.org/10.5281/zenodo.18947543); [article](https://www.nature.com/articles/s41597-026-07100-x), [units Table 1](https://www.nature.com/articles/s41597-026-07100-x/tables/1). Re-retrieved directly on 2026-10-20 NZDT; hashes and retrieval status are in `artifacts/source_verification_v2.json`. Original 1998 experimental report: [10.1111/j.1151-2916.1998.tb02662.x](https://doi.org/10.1111/j.1151-2916.1998.tb02662.x). Its raw Table 3 parameters are cited via the curated dataset; original sample conditions have not been independently recovered.

## Algorithm

1. Independently account for request text; resolve explicit C/K bounds and reject contradictions. Require an exact DOI + conductivity type + method + reported-range group. Never silently truncate a group exceeding the material limit.
2. Validate both parameter pairs and the reported range. Missing prerequisites exclude the record. Unknown conductivity type is never promoted to total.
3. Construct each record's measured LT/HT intervals, open at published T*. A single fit covers its measured range. Partial HT metadata does not become a single fit. T* outside the measured range does not extend evidence.
4. For every pair of fixed-regime intervals, intersect both measured ranges. With Ea in meV and A in K S/cm:

   `ln(sigma_i/sigma_j) = ln(A_i)-ln(A_j) - (Ea_i-Ea_j)/(1000*k_B*T)`

   `T_cross = (Ea_i-Ea_j)/(1000*k_B*(ln(A_i)-ln(A_j)))`

   Log-prefactor subtraction avoids overflow in A_i/A_j. A root must be positive, finite, strictly inside the common fixed-regime evidence and requested open interval, away from T*, numerically representable and have a sign change. Otherwise retain it as a rejected candidate or unresolved numeric review. Parallel/identical models have no isolated root.
5. Split the requested range at evidence limits, T*, accepted analytic roots and ±5 K review limits. Rank a point inside every open cell; evaluate boundaries separately. Plot resolution never decides the events or interval map.
6. Compare one-sided model order around T*. A fit-induced jump is `REGIME_BOUNDARY_DRIVEN_CHANGE`, never a continuous crossover. Exact T* is withheld (1e-6 K arithmetic equality tolerance). The 5 K neighborhood is an engineering review heuristic, not a scientific uncertainty interval.

The API limits selection to 12 materials, requested samples to 201, and selected temperatures to 20. Additional evidence/event/selected points are included in the response. Reported point values, original raw fields, validity intervals, rejected roots, warnings and code fingerprint are exported. Numerical ties are annotated at relative 1e-10; this tolerance is not experimental uncertainty. There is no global winner across source groups.

## Independently reproduced flagship

All rows below are bulk, two-probe AC, reported 600–1100 K, same source DOI.

| Row | Original formula | 700 K, LT sigma (S/cm) | 1000 K, HT sigma (S/cm) | T* (K) |
| --- | --- | --- | --- | --- |
| 1 | La0.95Sr0.05Ga0.95Mg0.05O2.95 | 0.00152279771378 | 0.03367431938647 | 805.5450205 |
| 2 | La0.95Sr0.05Ga0.9Mg0.1O2.925 | 0.00105664991471 | 0.04872339496037 | 830.3631709 |
| 3 | La0.95Sr0.05Ga0.85Mg0.15O2.9 | 0.000646360239378 | 0.06711958406591 | 874.9335546 |

Endpoint order changes **1 > 2 > 3** to **3 > 2 > 1**. Independent 60-digit Decimal/SI arithmetic is in `benchmarks/reference_v2.py` and `artifacts/rank_reversal_reference_v2.json`. Production agreement is tested at relative 2e-14 for conductivities; analytic roots at relative 2e-13.

Supported *model* roots: rows 1/2 at **776.4074250510 K** (LT/LT), 1/3 at **817.9098253678 K** (HT/LT), 2/3 at **854.2614663396 K** (HT/LT). Each is inside both selected published regimes and measurement ranges. They are mathematical switching points of curated fits, not measured crossing temperatures, fitted uncertainty bounds, new materials or corrections made by OxyProof.

Useful next action: check original sample conditions and repeat bulk-resolved conductivity measurements bracketing the predicted roots and reported transitions. The dataset does not establish humidity stability, atmosphere equivalence, density, lifetime, synthesis feasibility or a statistically validated winner.
