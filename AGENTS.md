# AGENTS.md — OxyProof / OSI Hackathon 2026

## 0. Mission and operating context

Build **OxyProof**, an evidence-grounded scientific research agent for screening **oxygen-ion-conducting oxide materials** using published experimental data, scientifically valid temperature-dependent conductivity calculations, and auditable agent decisions.

- Target event: Open Scientific Intelligence (OSI) Hackathon, October 21–22, 2026.
- Public event site: https://llmhackathon.github.io/
- 2026 agenda: https://llmhackathon.github.io/agenda/
- Published submission deadline: **2026-10-23 00:00 UTC = 2026-10-23 13:00 NZDT**. Organizer/Slack updates supersede static pages.
- Submission: the 2026 agenda describes a public social-media post, optional up-to-4-minute video/presentation, and up-to-one-page write-up. The site's `/submission/` page has historical dates/instructions: **do not silently treat it as the 2026 source of truth**. Verify the latest process in event Slack or attendee communication.
- Optimize for a judge-demonstrable, genuinely working vertical slice, reproducibility, scientific relevance, and transparent evidence. Avoid shallow multi-agent theater.

## 1. Hard scope

### Product promise

A researcher asks, for example:

> "Find oxygen-ion-conducting oxide candidates for operation at 600 °C. Calculate expected ionic conductivity using the source dataset's published model, show provenance, flag non-comparable observations, and explain what measurement would most improve confidence."

The system should:
1. Parse research goals and constraints, using a real LLM when configured.
2. Load and validate **real published scientific source records** (with an honest provenance trail).
3. Calculate conductivity with the **dataset's physically correct stated relationship**, unit handling, and regime boundaries.
4. Separate observations, model-derived calculations, heuristics, and proposed future experiments.
5. Produce an auditable candidate shortlist, calculation trace, explanatory comparison plots, and report.
6. Reject unsupported certainty and gracefully handle insufficient evidence.

### Canonical scientific starting point

Jang et al. (2026), *Charting the Landscape of Oxygen Ion Conductors: A 60-Year Dataset with Interpretable Regression Models*:
- Article: https://www.nature.com/articles/s41597-026-07100-x
- Dataset DOI: https://doi.org/10.5281/zenodo.18947543
- Dataset: https://zenodo.org/records/18947543 (`oxygen_ion_conductor_dataset.csv`)
- Published description: 483 oxide materials from 84 experimental reports with activation energies, prefactors, methods, provenance, and potentially distinct temperature regimes.

**Do not assume CSV column names, units, permitted uses, missingness, temperature ranges, or licensing. Inspect and record them before implementing any calculations.** If rights are ambiguous, use a documented retrieval script and user-provided files rather than redistribution until permission is confirmed.

Scientific equation quoted in the publication for the dataset's oxygen-ion conductivity records:

    sigma(T) * T = A * exp(-Ea / (R * T))

when `Ea` and `R` share compatible molar energy units; equivalently `Ea` in eV per carrier and `k_B` in eV/K where appropriate. Thus `sigma(T) = A/T * exp(-Ea/(R*T))`. Confirm dataset-specific units, phase/regime definitions, labels, and whether any published values require alternate handling **before coding**. The wrong counterexample `sigma(T) = A * exp(-Ea/(R*T))` is useful as an adversarial demo, but don't imply all literature or every transport model uses the same prefactor convention.

### Research boundaries

- Do **not** claim to discover a new material, experimentally measure anything, confirm a paper is erroneous without direct support, or provide validated uncertainty intervals if the data cannot justify them.
- Rankings are conditional screening outputs, **not experimental performance guarantees**.
- Extrapolations, regime ambiguity (including low/high-temperature transitions), bulk vs. total conductivity, atmosphere, preparation method, and missing metadata must be flagged explicitly.
- Missing evidence is an explicit `INSUFFICIENT_EVIDENCE` or equivalent typed outcome—not fabricated citations or silent fallback.
- No expensive DFT/MD training, autonomous lab control, or general-purpose chemistry platform during the 48-hour MVP.

## 2. Repository organization (target; adapt minimally to existing files)

    AGENTS.md
    README.md
    pyproject.toml
    uv.lock
    .env.example
    .gitignore
    backend/
      app/
        main.py                 # FastAPI endpoints
        schemas.py              # typed request/response contracts
        agents/                 # goal planner, evidence auditor, optional LLM adapter
        data/                   # import, provenance, data quality checks
        science/                # units, Arrhenius calculations, regime selection
        reports/                # audit/report construction
    frontend/                    # Vite/React + TypeScript judge demo
    scripts/                     # data retrieval, repeatable validation
    tests/                       # domain, API, data fixture, adversarial tests
    benchmarks/                  # baseline + cases + explicit methodology
    docs/
      PROJECT_BRIEF.md
      SOURCES.md
      SCIENCE_ASSUMPTIONS.md
      COMPETITION_RULES.md
      DECISIONS.md
      DEMO_SCRIPT.md
      SUBMISSION_CHECKLIST.md
    artifacts/                   # example deterministic outputs (no keys/private data)

Prefer **Python 3.12+**, `uv`, FastAPI, Pydantic, pandas/numpy and scientifically justified math libraries; Vite/React/TypeScript for the showcase. Do not add LangGraph or heavy infrastructure merely to claim multi-agent capability. A deterministic orchestration state machine with an optional real LLM adapter is preferable to fake agent calls.

## 3. Required engineering behavior

1. **Inspect first.** Read README, repo state, package manifests, git status, and current implementation before changing anything. Do not overwrite user changes or assume a clean repo.
2. **Actually build and test.** Do not deliver only architecture prose or pseudocode. Implement end-to-end verified slices each iteration.
3. **Source of truth.** Any event or dataset claim must include source URL, access date, and whether it was directly verified. Distinguish 2026 instructions from historical 2025 pages.
4. **Provenance.** Every science result carries dataset DOI/record ID, source row ID, input parameters and units, formula selection, code version, warnings, and deterministically computed result.
5. **No hallucinated integration.** No invented API responses, real LLM outputs, experiments, confidence intervals, citations, performance metrics, deployment URLs, or paid credits.
6. **Honest runtime modes.** Separate `REAL_LLM`, `OFFLINE_DETERMINISTIC`, and `UNAVAILABLE`; identify the selected mode prominently in UI and artifacts. Never label a deterministic rules engine as an LLM.
7. **Safety.** Secrets via environment only; never commit credentials or raw private user data. No arbitrary LLM-generated code execution, shell access, unsafe URL fetches, or unconstrained file paths. External API operations use timeouts, bounded retries, and limits.
8. **Reproducibility.** Lock dependencies, pin dataset version, log checksums, deterministic seeds, one-command bootstrap, unit tests and repeatable sample analyses.
9. **Scientific integrity.** Use explicit temperature and conductivity units; robust handling of Kelvin/Celsius, eV/J/mol, overflow/underflow, zero/negative inputs, absent regimes, and incomparable observations. Validate dimensional consistency with focused tests.
10. **Evidence over UI theater.** Every front-end ranking/report must come from backend calculations. Show data-source provenance, regime warnings and audit verdicts, not mocked placeholders described as live.
11. **Demo first.** Provide a reliable local demonstration that runs without external network once verified dataset/samples are present. API model calls are optional enhancements, not a dependency for showing real calculations.
12. **No forced publication.** Do not commit, push, create public repos, deploy, post on social media, pay for services, or register for an event without explicit user approval. Local commits only if requested.
13. **Respect licenses.** Verify dataset and third-party license before redistribution; if uncertain, document and use download-on-setup or appropriately attributed derived fixture.
14. **Report errors.** If network, package, API, or dataset fetch fails, report exact error and an honest fallback; don't say tests passed without running them.

## 4. Product acceptance gates

### G0 — Source & science grounding
- [ ] Confirm 2026 event timeline and note submission mechanism still requiring attendee verification.
- [ ] Inspect authoritative paper and actual dataset schema, units, provenance, relevant restrictions and exact model.
- [ ] Create `docs/SOURCES.md` and `docs/SCIENCE_ASSUMPTIONS.md` with citations and explicit unresolved assumptions.

### G1 — Real data / rigorous math
- [ ] Reproducible, license-compliant ingest of real material records.
- [ ] Unit conversions and conductivity calculation verified against independently computed reference values.
- [ ] Correct treatment or explicit exclusion of records with missing prerequisites or ambiguous temperature regime.
- [ ] Tests demonstrate detection of the deliberately incorrect no-`1/T` equation.

### G2 — Functional researcher workflow
- [ ] Research goal -> filtered candidates -> computed comparisons -> warnings -> citeable provenance -> exportable report.
- [ ] User-friendly UI with a real chart and material/evidence detail.
- [ ] Optional genuine LLM structured plan with a strict schema; offline mode clearly labelled.

### G3 — Quality demonstration
- [ ] At least three published-data-backed demo cases and three adversarial scientific tests.
- [ ] Baseline vs audited results with measured and reproducible metrics; never manufacture improvement percentages.
- [ ] Browser/API flow verified where environment permits; automated tests all run, failures disclosed.
- [ ] Deliver a concise judge-oriented story, brief demo script, and one-page report draft.

### G4 — Submission readiness (requires human action)
- [ ] User confirms registration and latest Slack submission channel/rules.
- [ ] Final public URL/repository, social-media post, appropriate video length, one-page write-up ready.
- [ ] Any irreversible/public action explicitly approved by owner.

## 5. Agent output protocol

At the end of every coding sprint, provide:

    SPRINT_STATUS=PASS|PARTIAL|BLOCKED
    EVENT_RULES_STATUS=VERIFIED|PARTIAL|BLOCKED
    SCIENCE_DATA_STATUS=VERIFIED_REAL|PARTIAL|BLOCKED
    REAL_LLM_STATUS=VERIFIED|NOT_CONFIGURED|FAILED
    OFFLINE_DEMO_STATUS=PASS|FAIL|NOT_RUN
    TEST_STATUS=PASS|FAIL|NOT_RUN
    SUBMISSION_READINESS=NOT_READY|PARTIAL|READY_FOR_HUMAN_ACTION

Then report: (1) exactly what changed; (2) runnable commands; (3) test commands and actual outputs; (4) real vs mocked components; (5) scientific sources and assumptions; (6) limitations/risks; (7) next highest-value actions; (8) whether anything was committed, pushed, or deployed. Never misrepresent partial validation as a pass.

## 6. Developer priorities

- P0: trustworthy data ingest + correct science + one real end-to-end decision trace.
- P1: convincing research UX + evidence audit + adversarial demo.
- P2: real model tool-use/structured planning + evaluation + final submission package.
- Cut P2 polish before sacrificing P0 reliability.
- Do not ask for confirmation for routine safe local changes. Ask only when blocked by missing credentials/rights or before actions requiring approval.
