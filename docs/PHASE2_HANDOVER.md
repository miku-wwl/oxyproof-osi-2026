# Phase 2 engineering handover — 2026-10-20 NZDT

```text
PHASE2_STATUS=PARTIAL
SCIENCE_INTEGRITY_STATUS=PASS
CONSTRAINT_SAFETY_STATUS=PASS
TEMPERATURE_DECISION_STATUS=PASS
RANK_REVERSAL_DEMO_STATUS=VERIFIED
REAL_LLM_STATUS=NOT_CONFIGURED
FULL_DATASET_STATUS=VERIFIED
FRONTEND_STATUS=PASS
BROWSER_E2E_STATUS=PASS
BENCHMARK_STATUS=PASS
JUDGE_DEMO_STATUS=READY
SUBMISSION_READINESS=PARTIAL
SPRINT_STATUS=PARTIAL
EVENT_RULES_STATUS=PARTIAL
SCIENCE_DATA_STATUS=VERIFIED_REAL
OFFLINE_DEMO_STATUS=PASS
TEST_STATUS=PASS
```

The complete local scientific workflow is implemented and verified. Overall PARTIAL reflects the unconfigured live LLM and unresolved attendee/eligibility/public-submission gates, not a failed offline computation. No live model call, experiment, new-material discovery, deployment or statistical accuracy claim is implied.

## 1. Changes and exact paths

- Fixed generated/manual goal synchronization and explicit text/control conflicts. Structured-only API temperatures no longer inherit an invented default-temperature constraint.
- Replaced keyword-only rejection with an independent span-coverage grammar. Humidity, wet air and other unresolved clauses fail closed, including when a model omits them.
- Added fixed-regime interval intersections, analytic pair roots, boundary-aware conditional ranking, numeric ties, evidence verdicts, raw-parameter provenance, exclusions and bounded next-action proposals.
- Added three allowlisted tools with a small planner/executor, strict schemas and independent checks. Provider prose cannot create scientific arithmetic or citations. No silent offline fallback.
- Added the real API-backed Temperature Decision Explorer, slider, log conductivity curves, regime bands, interval map, shared tie ranks, source navigation and JSON download.
- Added a frozen 49-case benchmark, independent Decimal references, real browser tests/capture, source re-verification, reproducible validation wrapper, MIT original-code license and submission drafts.

`artifacts/phase2_change_manifest.json` records all created/modified paths relative to baseline `6dea5cb87136744e6765f525777e54eb1b7426cc`, plus staged count and protected unchanged inputs. The exact list follows:

<!-- FILES_START -->
```text
 M AGENTS.md
?? LICENSE
 M README.md
?? THIRD_PARTY_NOTICES.md
 M artifacts/327c_bismuth_bulk.json
 M artifacts/600c_huang_bulk.json
 M artifacts/827c_cobalt_bulk.json
 M artifacts/ambiguous_regime.json
 M artifacts/benchmark.json
?? artifacts/browser/humidity-abstention.png
?? artifacts/browser/mobile-explorer.png
?? artifacts/browser/temperature-explorer.png
?? artifacts/browser_e2e_results.json
?? artifacts/demo_video_validation.json
?? artifacts/final_integrity_v2.json
?? artifacts/humidity_refusal_v2.json
 M artifacts/out_of_range.json
?? artifacts/phase2_change_manifest.json
?? artifacts/phase2_http_smoke.json
?? artifacts/phase2_validation.json
?? artifacts/rank_reversal_reference_v2.json
?? artifacts/real_llm_status_v2.json
?? artifacts/scientific_benchmark_v2.json
?? artifacts/source_verification_v2.json
?? artifacts/temperature_decision_flagship.json
 M backend/app/agents/llm.py
 M backend/app/agents/planner.py
?? backend/app/agents/workflow.py
 M backend/app/main.py
 M backend/app/reports/audit.py
 M backend/app/schemas.py
?? backend/app/science/decision_schemas.py
?? backend/app/science/temperature_decisions.py
?? benchmarks/build_cases_v2.py
?? benchmarks/evaluate_v2.py
?? benchmarks/reference_v2.py
?? benchmarks/scientific_cases.json
 M docs/COMPETITION_RULES.md
 M docs/DECISIONS.md
?? docs/DEMO_SCRIPT_V2.md
?? docs/EVALUATION_V2.md
?? docs/JUDGE_SCORECARD.md
?? docs/NOVELTY_AND_LIMITATIONS.md
?? docs/ONE_PAGE_SUBMISSION_V2.md
?? docs/PHASE2_HANDOVER.md
?? docs/REQUEST_GRAMMAR.md
 M docs/SCIENCE_ASSUMPTIONS.md
 M docs/SOURCES.md
?? docs/SUBMISSION_CHECKLIST_V2.md
?? docs/TEMPERATURE_DECISIONS.md
?? frontend/demo.config.ts
?? frontend/e2e/demo.capture.ts
?? frontend/e2e/research.spec.ts
 M frontend/package-lock.json
 M frontend/package.json
?? frontend/playwright.config.ts
 M frontend/src/App.test.tsx
 M frontend/src/App.tsx
?? frontend/src/TemperatureExplorer.tsx
 M frontend/src/style.css
 M frontend/src/types.ts
 M frontend/vite.config.ts
?? scripts/browser_e2e.py
 M scripts/fetch_data.py
?? scripts/phase2_demo.py
?? scripts/validate_v2.py
?? scripts/verify_demo.py
?? scripts/verify_sources_v2.py
?? tests/test_agent_workflow.py
?? tests/test_request_integrity.py
?? tests/test_temperature_decisions.py
 M tests/test_workflow.py
```
<!-- FILES_END -->

Original `PROJECT_BRIEF.md`, `PROMPT_01_CODEX.md`, the published fixture CSV and fixture manifest are unchanged. AGENTS.md only gains Phase 2 contracts. The one old conflict test now supplies the explicit manual goal needed to represent the intended contradiction after the default-goal bug fix.

## 2. Scientific algorithm and evidence

Full dataset: Jang et al., https://doi.org/10.5281/zenodo.18947543, v1, CC BY 4.0. Fresh network retrieval passed byte size, SHA-256, MD5 and exact 34-column/483-row validation. There are 452 distinct formula strings, not 483 unique formulas. The attributed 24-row offline fixture remains intact.

Full CSV SHA-256: `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34`.

Direct article and Table 1 rechecks confirm `sigma=A/T*exp(-Ea/(k_B*T))`, Ea in meV converted to eV, A in K S/cm, T in K and sigma in S/cm. Direct source HTTP evidence, access time and licensing are in `artifacts/source_verification_v2.json`. Nature's web reader returned a cookie-redirect 500; direct Python HTTPS retrieval succeeded. No article text or figures are redistributed.

Comparisons require exact source DOI + type + method + reported range. Each pair is intersected in a fixed published regime; analytic roots must be positive, finite, within common measured evidence, inside the requested interval and away from T*. A numeric sign change and representability check verifies the root. Source-range/T* boundaries and engineering ±5 K limits split open decision cells. Plot resolution does not determine them. Exact T* is withheld at 1e-6 K arithmetic tolerance; relative 1e-10 numeric ties are explicit. Neither tolerance is scientific uncertainty. A discontinuous fit-driven reversal has its own event type, tested with an explicitly synthetic counterexample.

Details: `TEMPERATURE_DECISIONS.md`, `SCIENCE_ASSUMPTIONS.md`, `REQUEST_GRAMMAR.md`.

## 3. Verified flagship

Source rows 1, 2, 3: DOI **10.1111/j.1151-2916.1998.tb02662.x**, bulk, two-probe AC, 600–1100 K, source location Table 3 in the curated CSV.

| Row | Original formula | sigma at 700 K, LT (S/cm) | sigma at 1000 K, HT (S/cm) |
| --- | --- | --- | --- |
| 1 | La0.95Sr0.05Ga0.95Mg0.05O2.95 | 0.00152279771378 | 0.03367431938647 |
| 2 | La0.95Sr0.05Ga0.9Mg0.1O2.925 | 0.00105664991471 | 0.04872339496037 |
| 3 | La0.95Sr0.05Ga0.85Mg0.15O2.9 | 0.000646360239378 | 0.06711958406591 |

Thus the conditional model order is **1 > 2 > 3 at 700 K** and **3 > 2 > 1 at 1000 K**. Independent 60-digit Decimal/SI computations agree with production within relative 2e-14. Exact source parameters, original formulas, units and both regimes are exported.

Continuous model roots: **776.4074250510 K** (rows 1/2, LT/LT), **817.9098253678 K** (1/3, HT/LT), **854.2614663396 K** (2/3, HT/LT). They are independently checked at relative 2e-13. Published T*: **805.5450205**, **830.3631709**, **874.9335546 K**, respectively. A model root is not an experimentally measured crossing or a validated uncertainty bound.

Interpretation: prefactor ratios and energy differences change the ordering as temperature and selected regimes change. Evidence supports this conditional model comparison. It does not establish equivalent atmospheres, preparations, densities, stability or uncertainty. Review the original report and repeat bulk-resolved measurements bracketing roots and T*.

## 4. Actual validation results

Final recorded command: `uv run --offline --no-sync python scripts/validate_v2.py --browser` → **PHASE2_VALIDATION=PASS**, all 14 command stages exit 0. Full command arrays, stdout/stderr and timings: `artifacts/phase2_validation.json`; individual logs: `.local/validation-v2/`.

| Check | Actual final output / result |
| --- | --- |
| Locked Python environment | `uv lock --check --offline` PASS |
| Backend lint and formatting | All checks passed; format check PASS |
| Backend tests | **140 passed, 1 warning in 9.24s; 0 failed, 0 skipped** |
| Frontend production build | TypeScript + Vite PASS, 1582 modules transformed |
| Frontend ESLint | PASS, zero warnings |
| Frontend DOM contracts | **8 passed**; mocked HTTP is explicitly labelled |
| Genuine Chromium E2E | **14 passed**, 0 skipped/unexpected/flaky; about 19 s |
| Original independent references | Four Decimal/SI reference values reproduced |
| Original offline demos | **OFFLINE_DEMO=PASS cases=5** on real fixture |
| Retained educational guards | **8 cases; unsafe baseline 1, audited 8** |
| Expanded scientific benchmark | **49 cases, 49 passed, 0 failed, 0 live model calls** |
| New offline demonstration | **PASS, FULL_DATASET, 483 records**, endpoint orders verified |
| Full source inspection | **483 rows, 34 columns, 84 source DOIs** |
| Separate fresh HTTP smoke | **7 checks PASS** at port 8020, full dataset and current calculation fingerprint |
| Official npm audit | **0 vulnerabilities**, inspection snapshot, not a security guarantee |
| Live LLM | **NOT_CONFIGURED**, no usable key/model pair; no paid call executed |

The one retained warning is Starlette's TestClient/httpx bridge deprecation. It was not suppressed; real urllib/Chromium HTTP checks also passed. Temporary failures and their fixes are documented in `EVALUATION_V2.md`: mock-helper nesting, a stale manual-conflict expectation, and a real legacy “conductivity” grammar regression caught by the combined pipeline. No failing final check was hidden. A one-off log-print command hit the Windows GBK console on a Unicode test-title character; the UTF-8 JSON report and actual test execution remained intact.

Runtime: Windows, Python **3.12.13**, uv **0.11.16**, Node **26.5.0**, npm **12.0.1**, Playwright **1.64.1**, bundled Chromium **156.0.8078.4**. Python and npm locks are preserved/updated appropriately. No fresh POSIX or public deployment validation was executed.

## 5. Benchmark and model boundaries

`benchmarks/scientific_cases.json` is a frozen hand-selected 49-case corpus with per-case ground-truth methodology. Independent Decimal math, manual evidence labels and explicitly synthetic counterexamples are separate from production. `artifacts/scientific_benchmark_v2.json` records successes/failures, corpus/reference/evaluator checksums, fixture scope and zero live model calls. The corpus uses the portable 24-row fixture; full 483-row ingestion and browser/API evidence are separate. Test counts overlap and must not be summed into a sample size. No statistical significance, held-out generalization or general scientific-accuracy claim is made.

Model adapter tests use explicitly labelled synthetic response IDs and mocked transport. They verify tool selection, strict arguments, exactly one bounded call, independent rejection of model-omitted humidity, changed bounds/tool, malformed plans and provider-text exclusion. They are not live integration evidence. No configured provider/model was invented, requested or purchased. A future live run should record model, response ID, validated arguments and outcome for screening, interval analysis and unsupported-constraint refusal.

## 6. Browser and media evidence

Browser flows: default screening; generated temperature and type edits; manual conflict; humidity refusal; flagship curves/slider; exact T* exclusion; continuous-root shared tie ranks; wrong equation; out-of-range refusal; DOI hrefs; downloaded JSON contents; 390×844 mobile overflow check; explicitly injected HTTP-503 failure. All other browser science requests use the real FastAPI server. DOI link targets were checked; publisher availability was not claimed. Screenshots under `artifacts/browser/` were visually inspected. This proves local Chromium behavior, not Safari, public hosting or mobile hardware.

The final capture is **204.4 seconds (3:24.4), 1440x1000, VP9/WebM, no audio**. All ten scene snapshots and a near-end frame were visually reviewed. The separate real UI/API no-voice capture is `.local/demo/oxyproof-phase2.webm` with captions, a scene log and an actual exported report. Exact runtime, size, codec, SHA-256 and capture calculation fingerprint are in `artifacts/demo_video_validation.json`. Representative scene frames are under `.local/demo/frames`; visual review covers intro, both endpoint orders, root/regime review, dimensional rejection, humidity refusal and provenance. Caption overlays are presentation text over real UI, not fabricated app results. The WebM contains no audio stream. No MP4 conversion, upload or public video submission is claimed.

## 7. Exact run commands

Run from `D:\workshop\oct\oxyproof-osi-2026`. For a clean setup with Python 3.12+, uv and Node installed:

```sh
python scripts/start.py
```

For subsequent no-network start after setup:

```sh
python scripts/start.py --offline
```

These default to port 8000; use one owned server per port. A prior sprint's service was left untouched. The **fresh Phase 2 service is already running at http://127.0.0.1:8020**, process 62576, with separately verified current source fingerprint and full dataset. Manual equivalent for that port after stopping the owned service:

```sh
uv sync --locked --link-mode copy
uv run --no-sync python scripts/fetch_data.py
npm ci --prefix frontend --no-fund --no-audit
npm run build --prefix frontend
uv run --offline --no-sync python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8020
```

Verification and portable demonstrations:

```sh
uv run --offline --no-sync python scripts/validate_v2.py --browser
uv run --offline --no-sync python scripts/phase2_demo.py
uv run --offline --no-sync python benchmarks/evaluate_v2.py
uv run --offline --no-sync python scripts/demo.py
```

On a new machine install the optional local browser once, then run/capture offline:

```sh
uv run --offline --no-sync python scripts/browser_e2e.py --install
uv run --offline --no-sync python scripts/browser_e2e.py
uv run --offline --no-sync python scripts/browser_e2e.py --record
uv run --offline --no-sync python scripts/verify_demo.py
```

`--install` requires network and places browser binaries on the repo drive under ignored `.local/ms-playwright`. Browser tests own port 8011 and refuse to reuse an existing server. The bootstrap commands are documented for PowerShell/POSIX; current execution evidence is Windows. Initial empty-machine Python/Node installation is a prerequisite, not performed by these scripts.

Fresh dataset/source checks (network):

```sh
uv run --offline --no-sync python scripts/fetch_data.py --force
uv run --offline --no-sync python scripts/verify_sources_v2.py
```

`uv --offline` blocks package retrieval, not these explicitly network-using scripts. Normal scientific analysis and demos use no network once files are present.

## 8. Artifacts and judge workflow

- `artifacts/temperature_decision_flagship.json`: full evidence-aware interval report and raw records.
- `artifacts/rank_reversal_reference_v2.json`: independent endpoint/root Decimal references, parameters, units and code metadata.
- `artifacts/humidity_refusal_v2.json`: actual fail-closed request outcome and proposed next measurement.
- `artifacts/scientific_benchmark_v2.json`, `artifacts/phase2_validation.json`, `artifacts/browser_e2e_results.json`, `artifacts/phase2_http_smoke.json`: executed evidence.
- `artifacts/source_verification_v2.json`, `artifacts/real_llm_status_v2.json`, `artifacts/demo_video_validation.json`: source/model/media verification boundaries.
- `.local/demo/oxyproof-phase2.webm`, `.local/demo/scene-log.json`, `.local/demo/exported-decision.json`: local capture and its actual export; intentionally ignored media.
- `DEMO_SCRIPT_V2.md`, `ONE_PAGE_SUBMISSION_V2.md`, `NOVELTY_AND_LIMITATIONS.md`, `JUDGE_SCORECARD.md`, `SUBMISSION_CHECKLIST_V2.md`: judge/submission drafts. One-page text is concise but not a verified typeset PDF.

Fresh browser story: flagship preset → 700 K → 1000 K → inspect continuous root and T* → wrong-formula audit → manual humidity request and refusal → inspect source parameters → export. The source-scope and runtime-mode labels remain visible; no results are preloaded.

## 9. Rights, uncertainties and submission blockers

Original code receives MIT at the owner's Phase 2 request; third-party rights/attribution remain separate. Owner review is still appropriate before publishing the new license and claims. Dataset CC BY 4.0 is directly verified; article CC BY-NC-ND rights are separate. No article figures/text, credentials or browser binaries are added to distributable files.

Atmosphere, preparation, density, original-source experimental conditions, fit uncertainty, phase stability, humidity stability and durability remain unknown. Conditional source grouping is not proof of complete experimental comparability. These limits remain visible and unsupported requirements abstain.

Public 2026 agenda was directly reverified: deadline **October 23, 00:00 UTC = 13:00 NZDT**, optional up-to-four-minute video/presentation and up-to-one-page write-up in a social submission. Current Slack channel/form/tags, registration/team, final rubric and eligibility of October 20 pre-event development need human confirmation. The initial MVP and Phase 2 began before October 21; that timeline is disclosed. No organizer message, registration or submission occurred.

## 10. Git and remaining priorities

Branch `main`, HEAD remains **6dea5cb87136744e6765f525777e54eb1b7426cc**. Phase 2 changes are local, unstaged and uncommitted. No Phase 2 commit, push, deployment, media upload, payment or publication was performed. The GitHub URL still refers to the previously approved MVP until the owner authorizes new delivery.

1. Confirm registration, latest Slack process and pre-event-work eligibility.
2. If an owner-provided key/model pair becomes available, run the three bounded live scenarios and preserve real provider identifiers; keep current NOT_CONFIGURED claims until then.
3. Review original-source sample conditions and prioritize bulk-resolved measurements bracketing predicted roots/T* and any humidity requirement.
4. Review/license/claim-check the final media and concise write-up, typeset one page if required, then explicitly authorize Phase 2 delivery and public submission.
