# Final validation - 2026-10-20 NZDT

**Technical regression PASS. Overall release CONDITIONAL_GO for owner review; not submitted.** `artifacts/final_validation.json` contains the actual command results, counts, environment and limitations. Earlier validation documents are historical snapshots.

## Executed results

| Check | Actual result |
| --- | --- |
| `python scripts/start.py` | Locked sync, pinned cached CSV, clean npm ci (271 packages), production build and ready localhost server PASS |
| `python scripts/start.py --offline` | Fresh owned server ready on 127.0.0.1:8000, no sync/download/build |
| `uv run --offline --no-sync python scripts/validate_v2.py --browser` | All 14 command stages PASS |
| pytest | **145 passed, 0 failed, 0 skipped, 1 warning in 10.58s** |
| Frontend component contracts | **8 passed**, mocked fetch; not browser evidence |
| Production TypeScript/Vite build | PASS; 1582 modules, 4.54s |
| ESLint | PASS with max-warnings 0 |
| Ruff check / format | PASS; latest added optional PDF script also checked; 45 files formatted |
| Genuine Chromium | **14 passed, 0 skipped, 0 unexpected, 0 flaky**, 23.1s; desktop 1440x1000, mobile 390x844 |
| Browser traces | 14 actual traces retained under ignored `.local/e2e-results`; screenshots under `artifacts/browser/` |
| Original demonstrations | **5/5 PASS**, real 24-row fixture |
| Original educational guards | **8 cases, unsafe baseline 1, audited 8**; intentionally unsafe comparator |
| Scientific integrity corpus | **49/49 PASS**, 0 failed, selected/partly synthetic, 0 live model calls |
| `scripts/phase2_demo.py` | PASS, full 483-record dataset, endpoint orders verified |
| `scripts/verify_final_science.py` | PASS: three independent roots, six endpoint values, both sides of all roots, 40/80-digit stability |
| `scripts/smoke.py` | **6/6 PASS**, real HTTP to fresh port 8000 |
| Additional real HTTP interval request | PASS; current code fingerprint, uncertainty qualification, orders 1>2>3 and 3>2>1; `final_http_decision.json` |
| Full CSV fresh download | `fetch_data.py --force`: VERIFIED_REAL, 483 records, exact 34 columns, SHA-256 verified |
| Clean cached Python environment | Created `.local/repro-venv`, `uv sync --locked --offline --link-mode copy`: 30 packages installed; fresh environment phase2 demo PASS |
| Final video | Actual record test 1 passed; 204.76s, 1440x1000, 25 fps, no audio; 11 representative frames inspected |
| One-page PDF | A4, 1 page, 5357 bytes; text checks, pdfinfo and actual Poppler PNG inspection PASS |
| Live LLM | NOT_CONFIGURED; no API key/model pair or .env; **0 live calls** |

The backend warning is the existing Starlette TestClient/httpx deprecation; it was not suppressed. Playwright reports NO_COLOR ignored when FORCE_COLOR is set. npm reports esbuild postinstall blocked by existing allowScripts policy; actual builds work, and no security setting was weakened. PDF rendering reports no display font for Symbol; the rendered ASCII page has no missing glyph/layout defect. Optional PDF dependency installation fell back from hardlinks to copies across drives. None is concealed as a zero-warning environment.

A temporary Ruff check on the copied PDF helper caught an unbound loop closure; its list is now bound explicitly and the final lint/format checks pass. The reference calculation, runtime and benchmark expectations were not changed to satisfy a test. No final failing check is known.

## Mandatory safety coverage

All referenced pytest cases ran within the 145 passing tests; browser cases ran against the real API except the explicitly injected failure.

| Case | Exact evidence |
| --- | --- |
| 1. Valid 600 C bulk | `test_api.py::test_screen_contract`; browser default screening |
| 2. UI temperature edit | browser `generated goal follows temperature controls` |
| 3. UI conductivity type edit | browser `generated goal follows conductivity type` |
| 4. Manual conflict | `test_request_integrity.py::test_api_precise_conflict_codes`; browser manual contradictions |
| 5. Humidity | `test_all_unresolved_clauses_fail_closed`; browser humidity refusal |
| 6. Long-term phase stability | same parametrized test, exact `that remain phase-stable during long-term cycling` clause |
| 7. Extra unknown constraints | same test: density, oxygen pressure, cost, lifetime, invented word and shell instruction |
| 8. Incomplete parameters | `test_science.py::test_real_ambiguous_regimes_abstain` (partial published HT prerequisites), invalid numeric/units tests |
| 9. Missing T* | benchmark `missing_transition`; real ambiguous-regime cases |
| 10. Outside measurement range | `test_extrapolation_opt_in_never_ranks`; interval outside-range test; browser refusal |
| 11. Boundary neighborhood | benchmark `near_transition_review`; exact transition test; browser affected-row withholding |
| 12. Analytical reversal | independent final science artifact; `test_real_flagship_independent_ordering_and_math` |
| 13. Root outside evidence | `test_root_outside_joint_evidence_rejected`, explicitly synthetic counterexample |
| 14. Cross-study refusal | `test_interval_refusals` rows [1,39]; group separation test |
| 15. Wrong formula | `test_wrong_formula_dimensional_failure`; browser wrong-formula audit |
| 16. Missing/corrupt data | `test_missing_full_file_explicitly_labels_fixture`, `test_corrupt_full_file_never_silently_uses_fixture`, `test_unavailable_data_returns_explicit_503` |
| 17. Invalid model arguments/tool | `test_malformed_or_unsafe_model_plan_rejected`; bounds/tool conflict contracts |
| 18. Provider failure | `test_provider_failure_never_becomes_offline_success`, explicit UNAVAILABLE; browser synthetic 503 display |

Free-form provider prose is ignored; only validated typed arguments enter scientific tools. Source DOIs and quantities come from deterministic output. Model contract tests are mocks, never live model acceptance. Exact acceptance prompts A/B include benign phrasing outside the current grammar and fail closed; Scenario C also abstains. No claim of arbitrary natural-language support is made.

## Reproduction

From the repo root, with Python 3.12+, uv and Node 22.12+ installed:

```sh
python scripts/start.py
# Subsequent network-free start:
python scripts/start.py --offline
uv run --offline --no-sync python scripts/validate_v2.py --browser
uv run --offline --no-sync python scripts/phase2_demo.py
uv run --offline --no-sync python scripts/verify_final_science.py
uv run --offline --no-sync python scripts/smoke.py
```

Initial browser setup, if needed: `uv run --offline --no-sync python scripts/browser_e2e.py --install` (explicit network download). Source/download rechecks use `scripts/verify_sources_v2.py` and `scripts/fetch_data.py --force`; uv's offline flag only disables package fetching, not explicitly network-using scripts.

Optional one-page PDF reproduction (separate local environment, no application lock changes):

```sh
uv venv .local/pdf-venv --python 3.12
uv pip install --python .local/pdf-venv/Scripts/python.exe reportlab==5.0.1 pypdf==6.21.1
.local/pdf-venv/Scripts/python.exe scripts/build_submission_pdf.py
pdfinfo output/pdf/oxyproof-one-page-submission.pdf
pdftoppm -scale-to 1500 -png -singlefile output/pdf/oxyproof-one-page-submission.pdf .local/submission-page
```

Rerendering resets visual acceptance to pending; inspect the new page before delivery. POSIX uses the environment's `bin/python` instead of `Scripts/python.exe`; that platform was not executed. Clean Windows cached-environment reproduction passed, not a fresh OS installation or a public deployment. Initial Python/Node/uv availability remains a prerequisite.

Dataset SHA-256: `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34`; 483 records / 34 columns / 84 source DOIs / 452 distinct formula strings. The 24-row fixture and its manifest remain byte-for-byte unchanged. Full mode and fixture mode are distinct in API/UI/exports. Invalid full data never silently fall back. Python and npm application lockfiles are unchanged.

Environment: Windows 11 build 26200; system Python 3.13.9, application CPython 3.12.13, uv 0.11.16, Node 26.5.0, npm 12.0.1, Playwright 1.64.1, Chromium 156.0.8078.4. No POSIX/browser-family/public-cloud generalization is inferred.
