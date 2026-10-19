# Science contract

Verified 2026-10-20 against [Methods](https://www.nature.com/articles/s41597-026-07100-x) and [Table 1](https://www.nature.com/articles/s41597-026-07100-x/tables/1). Dataset: [10.5281/zenodo.18947543](https://doi.org/10.5281/zenodo.18947543).

For these curated parameters:

```
sigma(T) = (A / T) exp(-Ea / (k_B T))
T[K] = temperature[degC] + 273.15
Ea[eV] = Ea[meV] / 1000
A: K S/cm; sigma: S/cm
k_B = (1.380649e-23 / 1.602176634e-19) eV/K
R = 1.380649e-23 * 6.02214076e23 J/(mol K)
```

Dividing A by T is dimensionally required for this convention. Reusing the same numeric prefactor in the no-1/T expression produces a quantity in **K S/cm**, not conductivity. The adversarial display shows this dimensional failure and the numeric ratio relative to sigma, in **K**. It never calls the wrong expression a valid alternative conductivity. Other literature conventions are outside this dataset contract.

The paper's derivation assumes temperature-independent mobile-defect concentration for relating diffusion and conductivity activation energies. We use its curated effective model; we neither refit source plots nor infer defect chemistry or new compounds.

## Regimes and evidence

- Only complete low/high pairs with a positive transition can select LT for T<T* and HT for T>T*. Exact T* abstains; a 5 K neighborhood warning is an engineering review heuristic, not an uncertainty interval.
- Any partial HT metadata (including the six anomalous rows in SOURCES) abstains. No guessed breakpoint or sentinel interpretation.
- Out-of-measurement-range requests abstain by default. Explicit extrapolation computes separately, labels `EXTRAPOLATED`, and gives no rank. No phase stability beyond a reported range is asserted.
- T* outside the reported range is a review warning, not evidence that the paper is wrong. The two observed rows are 79 and 280. Within a known range and a defined regime a calculation may still be made.
- Missing/invalid numeric parameters, nonfinite inputs, T<=0 K and unrepresentable floating-point results refuse calculation.
- Sort **within exact source DOI + conductivity type + measurement technique + reported range** only. These are provisional comparison groups. Missing atmosphere/preparation/density means even a group rank is conditional, with mandatory review. There is no cross-study winner or global rank.
- Unknown conductivity type never becomes total. Bulk and total are never combined.
- Model-derived values are not observed conductivities at the requested temperature. The raw CSV contains fitted parameters and source locations, not point measurements or validated error bars. No statistical confidence interval is generated.
- Proposed measurement advice is an explicit heuristic: check original conditions, separate bulk/grain boundary, and repeat measurements near target temperature or unresolved transition. No execution or quantitative expected information gain is claimed.

## Independent numeric validation

`scripts/reference_values.py` uses 60-digit Decimal arithmetic and SI constants, independently of the production calculator. Executed references (rounded here; full decimal strings in `artifacts/reference_values.json`):

| Original row | T (K) | Regime | Ea (meV) | A (K S/cm) | sigma (S/cm) |
| --- | --- | --- | --- | --- | --- |
| 1 | 700 | LT | 772 | 385385.727 | 0.00152279771377997559 |
| 1 | 873.15 | HT | 634 | 52785.93227 | 0.0132438119864429252 |
| 39 | 1100 | single | 831.6919733 | 1107333.313 | 0.155737064991434737 |
| 483 | 600 | single | 855.8621639 | 269310998.1 | 0.0290520689988645706 |

Production values agree within relative tolerance 2e-14 in focused tests. An additional independent algebraic test uses SYNTHETIC_TEST_ONLY parameters Ea=k_B*T*ln(2), A=2*T so sigma=1 S/cm. This validates arithmetic on published parameters, not experimental truth.
