# Scientific acceptance - 2026-10-20 NZDT

**SCIENTIFIC_CLAIMS_STATUS=PASS; SCIENCE_SOURCE_STATUS=PARTIAL; CROSSOVER_VALIDATION_STATUS=PASS.** Arithmetic and qualified showcased claims pass. Independent verification of the original experiment's full methods and Table 3 remains incomplete. This acceptance does not establish experimental superiority.

## Source evidence matrix

All sources below were accessed October 20, 2026 NZDT. Retrieval times, HTTP failures and hashes are in `artifacts/source_verification_v2.json` and `artifacts/primary_source_acceptance.json`.

| Claim or field | Evidence class | Directly inspected evidence / limit |
| --- | --- | --- |
| Dataset equation, parameter units, curation | VERIFIED_FROM_PRIMARY_SOURCE | [Jang et al. Methods](https://www.nature.com/articles/s41597-026-07100-x) and [Table 1](https://www.nature.com/articles/s41597-026-07100-x/tables/1), direct HTTPS 200. Primary source for the dataset's methodology, secondary to the 1998 experiment. |
| Dataset version, rights, downloadable CSV | VERIFIED_FROM_PRIMARY_SOURCE | [Zenodo v1 metadata](https://zenodo.org/api/records/18947543), CC BY 4.0; fresh file checksum verified. |
| Original article identity | VERIFIED_FROM_PRIMARY_SOURCE | [Publisher abstract](https://ceramics.onlinelibrary.wiley.com/doi/abs/10.1111/j.1151-2916.1998.tb02662.x) and [author institutional record](https://scholarcommons.sc.edu/emec_facpub/82/): Huang, Tichy and Goodenough, J. Am. Ceram. Soc. 81, 2565-2575 (1998). Publisher also displays a 2005 online-publication date; the print citation is 1998. |
| General original-paper context | VERIFIED_FROM_PRIMARY_SOURCE | Abstract describes oxide-ion transport, composition/phase relationships and different temperature regimes. Its other-composition stability/pressure statements are **not assigned to rows 1-3**. No abstract number is used to validate these rows. |
| Row formulas, DOI, type, method, parameters, range, T*, source locator | VERIFIED_FROM_CURATED_DATASET | Exact CSV strings, source rows 1-3; original Table 3 not independently inspected. Curated fit values may reflect source authors' reassessment; do not call them independently transcribed original-table values. |
| Row-specific atmosphere / oxygen partial pressure | NOT_VERIFIED | Not a dataset column; full original methods unavailable. Abstract does not prove the conditions for these three samples. |
| Sample fabrication, heat treatment, electrodes, density, porosity, microstructure | NOT_VERIFIED | Not established for these rows. Do not infer identical preparation from a shared DOI. |
| Parameter covariance, measurement errors, reproducibility, root uncertainty | NOT_VERIFIED | No validated uncertainties available to this implementation; no error bars or confidence intervals. |
| Humidity tolerance, long-term cycling, device performance | NOT_VERIFIED | Not supported by the curated fields or the inspected primary evidence. Requests abstain. |

The DOI and PDF attempts returned HTTP 403 through direct Python retrieval. The web reader's PDF request reached the publisher **abstract**, not a PDF. The institutional record links to the publisher and provides no accessible manuscript. No authentication, access-control circumvention or full-text redistribution was attempted. Thus full text is **inaccessible in this session**, not proven universally unavailable.

## Exact flagship inputs

All three curated records: DOI `10.1111/j.1151-2916.1998.tb02662.x`, source `Table 3`, `bulk`, `two-probe AC`, measured range `600 - 1100 K`. Ea/EaHT are meV; A/AHT are K S/cm; T* is K.

| Row | Original CSV formula | Ea | A | EaHT | AHT | Curated T* |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | La0.95Sr0.05Ga0.95Mg0.05O2.95 | 772 | 385385.727 | 634 | 52785.93227 | 805.5450205 |
| 2 | La0.95Sr0.05Ga0.9Mg0.1O2.925 | 996 | 10962599.59 | 673 | 120090.3914 | 830.3631709 |
| 3 | La0.95Sr0.05Ga0.85Mg0.15O2.9 | 1118 | 50677875.87 | 780 | 572632.8272 | 874.9335546 |

These are a reasonable **conditional model comparison** under the implemented exact DOI/type/method/range grouping. That policy controls some obvious incompatibilities but cannot prove experimental equivalence. Preparation, porosity, contacts, atmosphere and microstructure could affect measured transport; this is a reason for original-method review, not a claim that such differences were observed here. No universal best material or experimentally superior sample follows.

## Independent reference calculation

Run `uv run --offline --no-sync python scripts/verify_final_science.py`. `artifacts/scientific_acceptance.json` records the actual result, exact raw inputs, full Decimal results and code version. The separate reference uses CSV strings, 80-digit Decimal arithmetic and SI joules, without production constants, math functions or regime selection. 40/80 digit roots agree within 1e-30 K as an arithmetic stability check.

`Ea_J = Ea_meV * 0.001 * 1.602176634e-19`; `k_B = 1.380649e-23 J/K`; `sigma = A/T * exp(-Ea_J/(k_B*T))`. The shared 1/T cancels in pair ratios: `T_root=(Ea_i_J-Ea_j_J)/(k_B*ln(A_i/A_j))`. Compatible units are essential. Celsius inputs convert by +273.15; the showcase uses kelvin.

| Pair / fixed regimes | Open common evidence interval (K) | Technical root (K, rounded here) | Order at root - 1 K | Order at root + 1 K |
| --- | --- | ---: | --- | --- |
| 1/2 LT/LT | (600, 805.5450205) | 776.407425051022 | 1 > 2 > 3 | 2 > 1 > 3 |
| 1/3 HT/LT | (805.5450205, 874.9335546) | 817.909825367825 | 2 > 1 > 3 | 2 > 3 > 1 |
| 2/3 HT/LT | (830.3631709, 874.9335546) | 854.261466339589 | 2 > 3 > 1 | 3 > 2 > 1 |

All roots are finite, positive, strictly inside joint measured/fixed-regime evidence and distinct from all affected T*. Pair conductivity equality and sign/order changes were checked independently. Production agreement uses relative root tolerance 2e-13, conductivity tolerance 2e-14; these are **software tolerances**, not measurement uncertainty.

| Row | Calculated sigma at 700 K, LT (S/cm) | Calculated sigma at 1000 K, HT (S/cm) |
| --- | ---: | ---: |
| 1 | 0.00152279771378 | 0.03367431938647 |
| 2 | 0.00105664991471 | 0.04872339496037 |
| 3 | 0.000646360239378 | 0.06711958406591 |

## Interpretation and permitted demo claims

The conditional ranking changes because activation-energy differences and prefactor ratios interact with temperature and the selected fits. At 700 K the order is 1 > 2 > 3; at 1000 K it is 3 > 2 > 1. The three accepted events are **within-fixed-regime continuous analytical crossings**. A branch-selection change at curated T* is a separate event; continuity is never presumed. Exact T* is withheld. An engineered discontinuous fit-change counterexample, unstable/absent root handling and roots outside evidence are tested separately. No out-of-range extrapolation enters measured-only interval ranking.

**Model-derived crossover temperatures; uncertainty bounds unavailable; experimental confirmation required.** Public event headings/captions use approximately **776, 818 and 854 K**. Exported JSON, technical interval details and cursor sample coordinates retain reproducible numeric values; displayed coordinate digits are not physical precision. The +/-5 K neighborhood and numerical tie tolerances are engineering heuristics, not error bars.

Allowed: computational interpretation of published curated fits; conditional ranking reversal; dimensional rejection of reusing this A without 1/T; refusal of unsupported constraints; auditable provenance; proposed follow-up measurements. Prohibited: measured crossover, new experiment/material, verified humidity/cycling stability, proven original-paper error or statistical confidence. Suggested next work is to obtain full original methods and remeasure bulk-resolved conductivity bracketing roots/T*, reporting sample conditions and fit uncertainties. No experiment has been executed.
