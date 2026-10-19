# CODEX PROMPT 01 — OxyProof: Source Verification + Working Scientific MVP

**Recommended agent:** Codex (reasoning/high-effort coding mode, if available).
**Execution target:** Current repository `oxyproof-osi-2026`; complete a substantial engineering sprint now, not only a plan.

You are the principal software engineer, materials-data scientist, research agent architect, and hackathon tech lead for OxyProof — an evidence-grounded Oxygen-Ion Conductor Discovery and Scientific Verification Agent for the Open Scientific Intelligence Hackathon (October 21–22, 2026).

Read `AGENTS.md` from the repository root and follow it. If not present, stop and report it; do not invent its contents. Preserve any existing work; do not start a new repository if one already exists.

## The competition & scientific foundation

Official event: https://llmhackathon.github.io/
Official 2026 agenda: https://llmhackathon.github.io/agenda/
Official registration: https://luma.com/ku88xh92
2026 published deadline: Oct 22, 2026, 7 PM Central Daylight Time = Oct 23, 2026, 00:00 UTC = Oct 23, 2026, 13:00 NZDT.
Do **not** silently use the event website's `/submission/` page as the 2026 authoritative deadline—it contains historical instructions/dates. Record uncertainty about final submission mechanics in `docs/COMPETITION_RULES.md` and mark Slack confirmation required.

Canonical scientific foundation:
- Paper: https://www.nature.com/articles/s41597-026-07100-x
- Dataset: https://zenodo.org/records/18947543
- DOI: 10.5281/zenodo.18947543
- Published description: 483 oxygen-ion-conducting oxides, compiled from 84 reports, with Arrhenius activation-energy / prefactor data and source metadata.
- Reference form in paper: conductivity `sigma(T) * T = A * exp(-Ea / (R*T))`, **only after confirming actual data conventions**. Alternative units may require `k_B` instead of `R`. Handle two-regime materials, bulk-vs-total and record restrictions. Do not claim numerical validity until the schema is inspected and independent checks pass.

Product story: Researcher asks which oxygen-ion-conductor candidates may perform well at a specified operating temperature. OxyProof looks up *real* measured-source model parameters, computes temperature-dependent ionic conductivity, ranks only fairly comparable candidates, explains limitations, and generates an evidence trail. An adversarial toggle demonstrates why blindly applying the wrong Arrhenius prefactor equation is scientifically misleading. The product is a research screening assistant, not a claims-of-new-discovery engine.

## Your tasks — do them, don't only write a proposal

### A. Preflight and evidence grounding (must finish before science code)
1. Inspect local cwd, git status, existing code and `AGENTS.md`, OS/runtime/toolchain; do not reset or overwrite unrelated work.
2. Verify the official competition timeline, eligibility basics, prior awards/project patterns, official submission instructions (clearly distinguish 2026 agenda from historical `/submission/`). Record source URLs, accessed dates and unresolved organizer/Slack questions.
3. Retrieve the **actual source CSV** (122.7 KB) from its Zenodo record when accessible. Inspect its real field names, dtypes, missing values, metadata, temperature regions, uncertainty, references, prefactor units, activation energy units, usage license and checksum. Read the relevant methods of the publication.
4. Define a **small, honest, versioned real-data fixture** only if license permits redistribution; otherwise implement download-at-bootstrap and keep an independently coded synthetic dataset solely for tests and explicitly label it `SYNTHETIC_TEST_ONLY`.
5. Produce `docs/COMPETITION_RULES.md`, `docs/SOURCES.md`, `docs/SCIENCE_ASSUMPTIONS.md`, `docs/DECISIONS.md`, and `docs/PROJECT_BRIEF.md`. Include a one-sentence judge pitch and an explicit novelty comparison with 2025 winners without unsupported "world's first" claims.

### B. Build a real scientific calculation engine
1. Bootstrap a reproducible Python backend using `uv`, FastAPI, Pydantic, numpy/pandas and light scientific math dependencies only where needed; lock packages.
2. Create an ingestion module that preserves source DOI/row identifiers, exact source data, schema checks, missing-value warnings, and data provenance.
3. Implement `conductivity_at_temperature` using the verified equation and dataset conventions, treating Celsius/Kelvin and activation-energy units correctly. Prevent overflow, invalid prefactors, negative temperatures and silent unit loss.
4. If multiple thermal regimes exist, select regimes according to verified metadata and refuse unsupported computation when regime determination is impossible. Distinguish observed/derived, predicted/extrapolated, and missing.
5. Add a baseline wrong-equation comparator, *only* as a clearly labeled educational adversarial demonstration. Include analytically independently validated unit tests of the correct and intentionally wrong formulas and report ratio/units only when meaningful.
6. Candidate matching, ranking and filtering must be traceable. Never silently equate bulk conductivity and total conductivity; make sorting limitations clear and preserve comparisons conditioned on exact sample/condition metadata.
7. Implement JSON audit schema containing `status`, `research_request`, `source`, `dataset_record_id`, `equation`, `inputs_with_units`, `computed_values_with_units`, `observations_vs_calculations`, `warnings`, `trace`, and `review_required`.

### C. Agent-driven workflow: real vs offline modes are non-negotiable
1. Implement a bounded, visible orchestration pipeline: parse goal -> retrieve records -> select legitimate scientific model -> compute -> audit -> rank or abstain -> present result.
2. Offer `OFFLINE_DETERMINISTIC` mode with honest labeling and real computation on real data. It must be fully functional without a paid key.
3. If a valid user-provided LLM API credential is already available, implement and exercise a real structured-output/tool planning adapter for `REAL_LLM` mode. Do not send confidential records/credentials elsewhere and never fake a successful call. If no credential exists, implement the adapter and report `NOT_CONFIGURED` rather than blocking the offline MVP.
4. Reject arbitrary AI-generated code execution; the LLM can select from allowlisted typed tools only. Add timeouts, input limits, malformed model response handling and explicit failure states.

### D. Deliver a judge-useful vertical slice (not just an API)
1. Build a compact, professional user experience using Vite + React + TypeScript connected to FastAPI. If a solid frontend already exists, reuse it.
2. UI minimum: goal input (and structured fallback), operating temperature (°C), evidence-backed candidate table, conductivity comparison plot, detailed provenance pane, explicit scientific warnings and correct-vs-incorrect equation comparison for a selected verified record, JSON report export, and clearly visible `OFFLINE_DETERMINISTIC` vs `REAL_LLM` badge.
3. Do not use static/mocked rank values in the UI. The displayed results must match backend responses and be testable. A clean initial demo should not rely on live external APIs once source data is available.
4. Record one fully reproducible baseline user walkthrough plus two scientifically adversarial workflows (wrong prefactor equation; inappropriate/ambiguous units or temperature regime) and make them accessible via seeded inputs.
5. Add `.env.example`, safe `.gitignore`, README with Windows PowerShell + POSIX setup, and one-command startup where practical.

### E. Quality and measurement
1. Run unit tests for data validation, science math, regimes, sorting, source citations, API contract and error cases.
2. Independently validate at least three mathematical values (explicit hand-worked or standalone reference code) and show the numbers in `docs/SCIENCE_ASSUMPTIONS.md`.
3. Establish an honest reproducible benchmark: naive/non-audited baseline vs verified system on labeled scientific error cases. Do not invent sample size, error reduction or accuracy percentage. If no measured benchmark yet, state `NOT_MEASURED`.
4. Run backend and frontend build/lint/tests, capture exact pass/fail counts, and run one HTTP smoke test. Browser E2E only if environment allows; never pretend it ran.
5. Capture one deterministic end-to-end audit JSON under `artifacts/` with a real published source and verify it is free of fabricated values.

## Scheduling and scope control

Treat this as a rapid scientific hackathon. First reach **G0 + G1 + working G2 slice**. Prefer quality and scientific correctness to complex RAG, massive ingestion, speculative LLM training, Kubernetes, Terraform, cloud deployment or unnecessary 4+ agent frameworks. It is acceptable to document unfinished polish, but deliver actual working code and tests, not a theoretical design. If source fields/rights/physical formula cannot be established, stop numerical product claims and clearly report a block, while still implementing safe scaffolding/test-only calculators.

## Non-negotiable approvals

Do not commit, push, make a repo public, deploy, publish a post, send emails, register, spend credits, or delete unrelated assets without explicit authorization from me. Safe local edits, downloads from public scientific sources, installs and automated tests are allowed. Read existing changes and preserve them.

## Final report format

Report exactly:

    SPRINT_STATUS=PASS|PARTIAL|BLOCKED
    EVENT_RULES_STATUS=VERIFIED|PARTIAL|BLOCKED
    SCIENCE_DATA_STATUS=VERIFIED_REAL|PARTIAL|BLOCKED
    SCIENCE_FORMULA_STATUS=VERIFIED|PARTIAL|BLOCKED
    REAL_LLM_STATUS=VERIFIED|NOT_CONFIGURED|FAILED
    OFFLINE_DEMO_STATUS=PASS|FAIL|NOT_RUN
    FRONTEND_STATUS=PASS|PARTIAL|BLOCKED
    TEST_STATUS=PASS|FAIL|NOT_RUN
    SUBMISSION_READINESS=NOT_READY|PARTIAL|READY_FOR_HUMAN_ACTION

Then provide:
- Exact files created/modified and high-level architectural decisions.
- Real-dataset DOI and checksum, confirmed fields/units/license and source limitations.
- What is truly operating vs stubbed or not configured.
- Commands to install, run, smoke-test and execute tests on Windows PowerShell and/or POSIX.
- Test results with counts, known failures, scientific caveats and evidence references.
- Demo steps and the next P1/P2 work that would improve judging outcomes.
- Confirmation that nothing was committed, pushed, deployed or published.

Make a substantial first engineering sprint now. Prioritize delivery over narration.
