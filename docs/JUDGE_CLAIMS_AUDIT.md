# Judge claims audit - 2026-10-20 NZDT

Claims below refer to the tested local implementation. Acceptance evidence is in `artifacts/final_validation.json`; test counts overlap with benchmark cases and are not independent scientific samples.

| Claim | Exact evidence | Qualification / remaining limit | Allowed public wording |
| --- | --- | --- | --- |
| Translate goals into scientific operations | `tests/test_agent_workflow.py::test_real_mode_tool_selection_contract_only`; `test_request_integrity.py`; `agents/planner.py` | Guided bounded English; exact free-text A/B acceptance prompts fail coverage. REAL_LLM transport is mocked, not live. | Bounded goals select three typed scientific operations; unfamiliar requirements abstain. |
| Compare valid temperature intervals | `test_temperature_decisions.py::test_no_ranking_outside_range_or_at_tstar`, `test_resolution_independence_and_determinism` | Exact DOI/type/method/range is provisional; missing experimental conditions remain. | Measured-only conditional comparisons over verified fit intervals. |
| Detect ranking reversal | `artifacts/scientific_acceptance.json`, `temperature_decision_flagship.json`; `test_real_flagship_independent_ordering_and_math` | Three curated published records, not new observations; no uncertainty bounds. | Computed conditional order changes from 1 > 2 > 3 at 700 K to 3 > 2 > 1 at 1000 K. |
| Distinguish crossings and T* | `test_discontinuity_never_mislabeled_continuous`, `test_root_outside_joint_evidence_rejected`; browser exact-boundary/tie checks | Synthetic discontinuity/outside examples are test-only. | Continuous model roots and fit-boundary changes are audited separately. |
| Expose wrong formula | `test_science.py::test_wrong_formula_dimensional_failure`; browser wrong-formula audit | Only this dataset's A convention; no accusation against a specific paper. | Reusing this A without 1/T fails the conductivity unit check. |
| Reject unsupported conditions | `test_request_integrity.py::test_all_unresolved_clauses_fail_closed`; humidity browser check | Safety by conservative refusal; no broad natural-language understanding. | Humidity, cycling and unknown constraints cannot disappear silently. |
| Export auditable evidence | browser `export contains real interval provenance and results`; captured `exported-decision.json` | Mathematical traceability, not external experimental verification. | JSON preserves source rows, parameters, units, warnings, raw roots and code fingerprint. |
| Suggest next evidence | `reports/audit.py`, `temperature_decisions.py`; actual refusal artifact | Deterministic heuristic proposals; no information-gain metric or execution. | Proposes original-method checks and measurements bracketing roots/T*. |
| Real scientific data | fresh `fetch_data.py --force`, `test_full_dataset_and_fixture_string_identity`, `dataset_inspection.json` | 483 records, 452 distinct formula strings; fixture is 24 records. | Published curated fit parameters with DOI/checksum provenance. |
| Reliable local application | 145 pytest, 8 mocked component contracts, 14 real Chromium checks, clean cached Python environment demo | Windows/Chromium only; 503 browser injection is synthetic; no public hosting test. | Tested local offline workbench with real API-backed plots and download. |
| Benchmark quality | `scientific_benchmark_v2.json`: 49 passed/49, 0 live calls; `docs/EVALUATION_V2.md` | Selected, partly synthetic, not external/held-out/representative or statistically significant. | Passed 49 targeted scientific integrity cases, including adversarial constraints and model-boundary checks. |
| Potential research impact | Integrated trace and refusal workflow demonstrated | No measured time saving, discovery yield or user study. | May help researchers prioritize evidence checks and follow-up measurements. |

Prohibited: "100% accurate scientific AI", experimentally discovered crossovers/materials, measured two-decimal certainty, verified humidity/cycling/device performance, statistical confidence, autonomous experimentation, live LLM success, or competition eligibility/submission without corresponding evidence.

Development began October 20 before the October 21-22 event. Do not conceal this or assert eligibility. See `RELEASE_GATE.md` for human gates.
