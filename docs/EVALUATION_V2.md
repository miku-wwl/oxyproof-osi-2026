# Scientific decision integrity evaluation v2

The frozen corpus is `benchmarks/scientific_cases.json`. Build/reference definitions are in `benchmarks/build_cases_v2.py` and `benchmarks/reference_v2.py`; production evaluation is separate in `benchmarks/evaluate_v2.py`. All commands run offline after setup:

```sh
uv run --offline --no-sync python benchmarks/evaluate_v2.py
uv run --offline --no-sync python -m pytest -q
uv run --offline --no-sync python scripts/browser_e2e.py
```

The measured v2 corpus has **49 cases**. Expected numbers use 60-digit Decimal arithmetic, exact SI constants and manually selected regime fields. Roots use independent Decimal logarithms. Refusal labels follow manually documented evidence/request rules. Plot-resolution invariance is a metamorphic check. Explicit synthetic pairs test continuous roots, a discontinuous regime-driven reversal and a root outside evidence. Invalid model plans are labelled synthetic contract cases, never live inference.

Coverage includes six real-data numeric references, source-group endpoint ranking, transition/extrapolation/absent-record handling, thirteen unsupported requirement categories, explicit conflicts, provenance wording, three real analytic roots, energy/prefactor unit equivalence, range gaps, resolution invariance and invalid model schemas. Exact categories, expectations and actuals are recorded per case in `artifacts/scientific_benchmark_v2.json`.

The evaluated scope is the attributed **24-row published fixture** for portability. Full-data ingestion/checksum/schema/equality and browser workflows are checked separately against the 483-row file. This corpus is hand-selected, not representative of unknown scientific tasks, not held-out model evaluation and not a statistical performance estimate. Test and benchmark scenarios overlap; their counts must not be summed into an independent sample size.

The original `benchmarks/evaluate.py` remains an **eight-case educational guard demonstration**, measuring 1/8 for an intentionally unsafe baseline and 8/8 for the audited system. It is not the v2 research benchmark, an improvement percentage or evidence of general LLM/scientific accuracy.

During implementation, two new pytest checks initially failed: a test helper wrapped an already mocked HTTP client, and a frozen default-temperature conflict case needed an explicit manual goal after the API bug was fixed. The helper and manually specified case were corrected; no production expected answers were copied from the evaluator. The final combined pipeline then caught a real compatibility regression: legacy demos used the benign noun “conductivity”, absent from the new allowlist. That noun was added and a regression case included; unsupported performance clauses still fail coverage. Initial lint found dense one-line statements; formatting corrected them. Final results and the remaining deprecation warning are recorded in `PHASE2_HANDOVER.md`.

Browser evidence is genuine Playwright Chromium against a separate local production FastAPI server. It covers 14 flows, including actual export download, desktop/mobile geometry and backend request values. One deliberately injected HTTP 503 is explicitly marked synthetic; other product calculations use the real API. DOI hrefs are checked, not publisher page availability. Model transports and component fetches are mocks solely in labelled tests. Live model evaluation remains NOT_CONFIGURED because no credential/model pair was available.
