# Fixed scientific guard benchmark

Run `uv run python benchmarks/evaluate.py`. The eight labels are explicit in source, from the source/model contract, and all are evaluated against real published rows or requests about those rows. Three anomalous raw values are not edited or invented. The synthetic **behavior** is a deliberately unsafe educational baseline: always produce a number, omit 1/T, ignore missing units and evidence boundaries.

Metric: count of expected decisions, with the required warning code for abstention cases. The naive implementation actually evaluates A*exp(-Ea/kBT) with low/single fields, guesses 600 C for absent/unitless temperature, ignores regime/type/range, and accepts the number as conductivity. Its numeric input/output trace is recorded. The final controlled formula case instead uses the same legitimately selected parameters on both sides to isolate the missing 1/T factor.

This is a small regression/guard demonstration, not a representative corpus, a blind benchmark, a model comparison, an estimate of experimental accuracy or a general percentage improvement. Baseline math is invalid even for the one case whose decision label it matches. No uncertainty interval, recall of a literature search, runtime speedup or external model score is claimed. Results are measured and stored in `artifacts/benchmark.json`.
