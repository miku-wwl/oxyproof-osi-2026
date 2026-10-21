# Scientific claims review - 21 October 2026 NZDT

SCIENTIFIC_CLAIMS_STATUS=PASS for the qualified production claims below. This does not mean original experimental conditions or model uncertainties have been verified.

| Production claim | Evidence | Qualification |
| --- | --- | --- |
| 483 published records, full pinned dataset | Current `/api/health`; `artifacts/dataset_inspection.json`; CSV SHA-256 `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34` | Records are not 483 independently unique compositions. Dataset source access was 20 October. |
| Dataset-specific conductivity calculation | `docs/SCIENCE_ASSUMPTIONS.md`, `docs/SCIENTIFIC_ACCEPTANCE.md`, production report equation/units | sigma=A/T exp[-Ea/(kB T)]. Ea meV -> eV; kB eV/K; A K S/cm; T K; sigma S/cm. Does not assert every transport model shares this convention. |
| 700 K order 1>2>3; 1000 K order 3>2>1 | `artifacts/temperature_decision_flagship.json`, genuine current browser footage, `review/exported-decision.json` | Exact curated DOI/type/method/range group; conditional model ranking, no global or experimentally proven superiority. |
| Model roots near 776/818/854 K | Engine event objects; independent 80-digit Decimal results in `artifacts/scientific_acceptance.json`; figure provenance | Actual roots 776.4074250510221 / 817.9098253678244 / 854.261466339589 K. Public values rounded. No experimental crossover or root uncertainty claim. |
| T* is separate from a continuous root | Event cards and archived source regimes | Affected row withheld at exact T*. +/-5 K is an engineering review heuristic, not an uncertainty interval. Plot branches are separated at T*. |
| Genuine DeepSeek tool choice | `artifacts/deepseek_live_acceptance.json`, byte-preserved original capture, provider IDs in current replay | Exactly three historical requests, all PASS for their specific scenarios; `deepseek-flash` is the reported alias. No new request or underlying weight-version guarantee. |
| B invokes interval analysis | Provider ID `8555b7b9-84f2-4553-b7ec-0041482bc9aa`, current replay, validated arguments | Named Huang group maps to predefined rows 1-3. Not autonomous material discovery. Deterministic engine supplies arithmetic and explanations. |
| C blocks unsupported constraints | Provider ID `36ab33a0-d258-4190-a5d4-4d867fd4fe0f`; execution trace; footage | Model proposed screening and reported two unsupported flags. Independent validator retains humidity/lifetime. Refusal origin BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR; zero candidates, empty execution args, no scientific calculation executed. No claim of a spontaneous model-only refusal. |
| JSON export succeeds | Actual IAB download `oxyproof-audit.json`; packaged copy `exported-decision.json`; source/model/ordering checks | Download occurred during scene 5; no synthetic export-success UI was added. |
| 255/12/21, 49/49, 3/3 | `artifacts/deepseek_regression.json`, `scientific_benchmark_v2.json`, `deepseek_live_acceptance.json` | Historical engineering runs. The benchmark is hand-selected, partly synthetic and overlapping; no representative accuracy or statistical significance. Production reran only 9 archived-replay checks, not the full suite. |

Source rows (original curated formula strings):

1. La0.95Sr0.05Ga0.95Mg0.05O2.95
2. La0.95Sr0.05Ga0.9Mg0.1O2.925
3. La0.95Sr0.05Ga0.85Mg0.15O2.9

All three are attributed to DOI `10.1111/j.1151-2916.1998.tb02662.x`, bulk, two-probe AC, reported 600-1100 K, Table 3 as curated by Jang et al. The original full methods/Table 3 were not independently inspected; neither common preparation nor atmosphere, density, porosity or fitted uncertainties is established. No humidity or 10,000-hour evidence is added.

Figure: `flagship-conductivity.png/.svg` is generated from actual archived engine curve points, with LT/HT plotted separately. No external article figure or generated scientific illustration is used. The plot CSV and source checksum are retained.

Primary source/rights record: [Jang dataset, CC BY 4.0](https://doi.org/10.5281/zenodo.18947543), [dataset methodology](https://www.nature.com/articles/s41597-026-07100-x), [original study](https://doi.org/10.1111/j.1151-2916.1998.tb02662.x). Original source verification was 20 October; current production verified cached evidence and a live local export on 21 October. Article rights remain separate; no article text/figures are redistributed.

Excluded claims: novel experimental material, new measurements, validated uncertainty intervals, measured crossovers, industrial performance, humidity stability, long-term lifetime, universal scientific accuracy and fresh inference during replay.

Older repository documents contain superseded pre-DeepSeek/no-public-release/human-gate statements. They are preserved as phase history; this package uses the actual public main state and the owner's latest registration/eligibility confirmations. Application/science source is unchanged by production.
