# Initial engineering sprint handover

```
SPRINT_STATUS=PARTIAL
EVENT_RULES_STATUS=PARTIAL
SCIENCE_DATA_STATUS=VERIFIED_REAL
SCIENCE_FORMULA_STATUS=VERIFIED
REAL_LLM_STATUS=NOT_CONFIGURED
OFFLINE_DEMO_STATUS=PASS
FRONTEND_STATUS=PARTIAL
TEST_STATUS=PASS
SUBMISSION_READINESS=PARTIAL
```

The scientific/data/API/offline slice works locally. Frontend production build, lint and six component tests pass; browser/visual E2E could not run because no connected browser exists. Optional LLM planning has a real provider adapter and mocked contract tests, but no credential/live call. Public event evidence is verified; attendee-specific Slack rules and pre-event-work eligibility still require human confirmation.

## What changed

- Python/uv/FastAPI/Pydantic backend, pinned source ingest with original row IDs and exact raw field strings, dimensional calculations and independently checked units, complete/partial regime handling, explicit abstention, within-source-group ranking, deterministic report/trace contracts, bounded optional single-tool LLM planner.
- Vite/React/TypeScript research workbench, structured fallback filters, source-group table and real API-based comparison/temperature plots, provenance/warnings/next-measurement pane, wrong-equation challenge, JSON export and explicit modes. No hardcoded candidate result values in product code.
- Attributed 24-row real CC BY 4.0 fixture plus manifest, pinned full-file retrieval and inspection, four Decimal/SI references, five deterministic sample audits, eight measured guard cases, local HTTP smoke, one-command startup and locked dependencies.
- Scientific/event sources, decisions, science assumptions, demo script, submission checklist and text write-up draft. Original AGENTS.md, PROJECT_BRIEF.md and PROMPT_01_CODEX.md remain unchanged; root README is expanded.

The exhaustive path list is machine-generated in **`artifacts/change_manifest.json`**. Local-only ignored outputs include `.venv`, `.local` (full CSV and source cache), `frontend/node_modules`, `frontend/dist`. No original article figures or full text are in the distributable fixture.

## Run and inspect

From `D:\workshop\oct\oxyproof-osi-2026`:

```sh
python scripts/start.py              # bootstrap/build/start, after installing uv + Python + Node
python scripts/start.py --offline    # subsequent local run; use one server at a time
```

Open http://127.0.0.1:8000; API docs http://127.0.0.1:8000/docs. The server started during handover listens only on 127.0.0.1:8000. README provides manual PowerShell/POSIX setup, exact test commands and HTTP request examples. POSIX execution is not verified.

Seed workflow: **600 °C screening → inspect row 1 → Wrong-formula audit → Unresolved regime → Outside measured range → Export audit JSON**. Use the 3-minute narration in `DEMO_SCRIPT.md`. Three real-data normal cases and two abstention artifacts can be regenerated with `uv run --offline --no-sync python scripts/demo.py`.

## Evidence and measured results

Dataset: [10.5281/zenodo.18947543](https://doi.org/10.5281/zenodo.18947543), CC BY 4.0, 122657 bytes, 483 rows / 34 columns / 84 source DOIs. SHA-256:

```
8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34
```

[Methods](https://www.nature.com/articles/s41597-026-07100-x) and [Table 1](https://www.nature.com/articles/s41597-026-07100-x/tables/1), directly retrieved 2026-10-20: Ea **meV**, A **K S/cm**, T **K**, sigma **S/cm**, using **A/T·exp(−Ea/kBT)**. Article rights differ from dataset rights. The CSV has 452 distinct formula strings, so 483 records must not be described as 483 distinct compositions.

**94 backend tests passed**, **6 frontend tests passed**, backend/frontend lint passed, production build passed. Four independent reference values agree to relative 2e-14. Genuine local HTTP smoke passed **6 checks** against all **483** loaded records. Five portable published-fixture demos passed. Eight fixed guard cases measured **1 correct decision for a deliberately unsafe baseline, 8 for the audited pipeline**; not a general accuracy/improvement claim. The baseline's real arithmetic trace is recorded and its units are explicitly invalid.

Full commands, outputs, recovered failures, the retained TestClient deprecation warning and exact verification boundaries are in `VALIDATION.md`. All five audit examples were checked against their raw fixture rows and current code fingerprint. Product computations are real/deterministic; model transport and frontend HTTP are mocked **only in explicitly labelled contract tests**. No experiments or live LLM calls have been simulated as product evidence.

## Limitations and next priorities

1. **P1: real browser review.** Verify desktop/mobile layout, all seeded flows, source navigation and export download when a browser is connected. Currently NOT RUN, so FRONTEND_STATUS remains PARTIAL.
2. **P1: original-source review.** Six rows lack complete HT metadata; unknown type remains unknown. Atmosphere/preparation/density and uncertainty are absent; even group ranks remain conditional. Review original papers and target-temperature measurements before making material claims.
3. **P2: genuine optional planning.** Owner supplies an environment credential/model, then run a real typed plan and record provider response ID and failure behavior. Current REAL_LLM_STATUS is NOT_CONFIGURED; no paid credits used.
4. **Submission: human checks.** Confirm registration, current Slack process, pre-event work eligibility, final rubric and media rules. Public 2026 deadline is **Oct 23, 13:00 NZDT** per the agenda; historical submission page is not authoritative. Draft is text only; no final video, public link or typeset one-page artifact exists.

No commit, staging, push, deployment, publication, registration, organizer message or spending was performed. The changes remain local for owner review.
