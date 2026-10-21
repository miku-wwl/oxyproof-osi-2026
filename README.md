# OxyProof

**A Temperature-Aware, Evidence-Grounded Materials Decision Agent.**

A local FastAPI + React research workbench. Uses the real [Jang et al. dataset](https://doi.org/10.5281/zenodo.18947543), explicit units and temperature regimes, conditional source-group rankings, abstention, provenance export and an adversarial wrong-equation demonstration. No cloud infrastructure or paid model is needed for deterministic analysis.

Phase 2 adds analytic rank-reversal analysis and the Temperature Decision Explorer; Phase 2.6 adds bounded research-tool planning and audited execution traces. **Phase 2.6.2: genuine DeepSeek acceptance VERIFIED, exactly 3 requests / 3 independent passes**, with source-backed screening, temperature-aware ordering and scientific abstention. Use explicitly labelled recorded-trace replay for repeatable demos; the paid sprint budget is exhausted. [Current acceptance](docs/DEEPSEEK_LIVE_ACCEPTANCE.md) · [judge demo](docs/DEEPSEEK_AGENT_DEMO.md). Offline analysis remains fully independent of model access. OpenAI and Ollama adapters are preserved; the [earlier Ollama native acceptance failure](docs/OLLAMA_REAL_AGENT_ACCEPTANCE.md) remains historical evidence.

## Start locally (Windows PowerShell or POSIX)

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/), Node.js 22.12+ (24/26 recommended for this lockfile), npm. Tested on Windows with uv-managed Python 3.12.13 and Node 26.5.0. No global package or Git settings are changed by these commands.

From the repository root, one-command bootstrap/build/start:

```sh
python scripts/start.py
```

Open **http://127.0.0.1:8000**. Stop the foreground server with Ctrl+C. Setup installs locked dependencies, retrieves/checks the pinned public full CSV, builds local assets and starts on loopback only. If full-data download is unavailable and no cached full file exists, the attributed real 24-row fixture is used and visibly labelled. A changed/invalid full file is rejected rather than silently replaced by a subset.

After setup, start with **no package sync, network download or build**:

```sh
python scripts/start.py --offline
```

Manual equivalent, valid in PowerShell and POSIX:

```sh
uv sync --locked --link-mode copy
uv run --no-sync python scripts/fetch_data.py
npm ci --prefix frontend --no-fund --no-audit
npm run build --prefix frontend
uv run --offline --no-sync python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Use `python3` in place of `python` where required on POSIX. The bootstrap remains Windows-verified; POSIX execution has not been run in this session. If port 8000 is occupied, stop your own server or explicitly choose another port in the manual uvicorn command and adapt the smoke script. Never terminate an unrelated process.

## Demo

Start with **Published rank reversal · rows 1 / 2 / 3** in the Temperature Decision Explorer. At **700 K**, model order is **1 > 2 > 3**; click **1000 K** for **3 > 2 > 1**. Original formulas, source group, curve regimes and conditional values come from the API. Inspect the continuous model crossings separately from published T*, move the backend-sample slider and export decision JSON. This interprets published evidence; no new material or experiment is claimed.

Guided screening text now follows temperature/unit/type controls. Editing it makes the goal manual; contradictory requirements are preserved and rejected. Try **Find bulk conductors at 600 C that survive 10% humidity**: unknown clauses return `UNVERIFIED_CONSTRAINTS` and proposed next measurements. See the [bounded request grammar](docs/REQUEST_GRAMMAR.md).

1. Click **600 °C screening**. Real published rows 1–3 are computed; group rank is 3, 2, 1 at 873.15 K.
2. Select **row 1**, inspect original DOI / Table 3, HT parameters and warnings. Its calculated conductivity is about **0.013243811986442925 S/cm**.
3. Click **Wrong-formula audit**. The no-1/T expression with the same A has units **K S/cm**, so it is rejected as conductivity. It never enters the ranking.
4. Click **Unresolved regime** or **Outside measured range**: the agent abstains with typed reasons. Explicit extrapolations are separate, warned and unranked.
5. Export audit JSON. Clear **Source row IDs** under structured filters to screen the entire loaded scope. Choose a source group; there is no global rank across different experiments.

[Full demo script and three published-data-backed examples](docs/DEMO_SCRIPT.md). Deterministic portable artifacts:

```sh
uv run --offline --no-sync python scripts/demo.py
uv run --offline --no-sync python scripts/reference_values.py
uv run --offline --no-sync python benchmarks/evaluate.py
```

Phase 2 reports, expanded corpus and genuine browser checks:

```sh
uv run --offline --no-sync python scripts/phase2_demo.py
uv run --offline --no-sync python benchmarks/evaluate_v2.py
uv run --offline --no-sync python scripts/browser_e2e.py --install
uv run --offline --no-sync python scripts/browser_e2e.py
uv run --offline --no-sync python scripts/browser_e2e.py --record
```

The optional `--install` downloads Chromium/FFmpeg to ignored `.local/ms-playwright` on the repository drive. Build assets first. Browser tests own a separate loopback server on port 8011 and do not reuse a stale server. `--record` captures a separate captioned no-voice demo to `.local/demo/oxyproof-phase2.webm`; its actual validation status is in the handover. It is not included in the normal test suite. [3–4 minute story](docs/DEMO_SCRIPT_V2.md) · [science algorithm](docs/TEMPERATURE_DECISIONS.md) · [benchmark method](docs/EVALUATION_V2.md).

## Verify

```sh
uv lock --check --offline
uv run --offline --no-sync python -m pytest -q
uv run --offline --no-sync python -m ruff check backend scripts tests benchmarks
uv run --offline --no-sync python -m ruff format --check backend scripts tests benchmarks
npm run build --prefix frontend
npm run lint --prefix frontend
npm run test --prefix frontend
```

With the API running:

```sh
uv run --offline --no-sync python scripts/smoke.py
```

HTTP example (PowerShell):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/screen -Method Post -ContentType 'application/json' -Body '{"row_ids":[1,2,3],"temperature":600,"temperature_unit":"C"}'
```

HTTP example (POSIX):

```sh
curl -s http://127.0.0.1:8000/api/screen -H 'Content-Type: application/json' -d '{"row_ids":[1,2,3],"temperature":600,"temperature_unit":"C"}'
```

Swagger contracts: http://127.0.0.1:8000/docs. Other routes: `/api/health`, `/api/catalog`, `/api/records/{row_id}`, `/api/records/{row_id}/curve`, `/api/records/{row_id}/adversarial`.

New typed endpoint: `POST /api/temperature-decisions` with `{"row_ids":[1,2,3],"temperature_min":600,"temperature_max":1100,"temperature_unit":"K","selected_temperatures":[700,1000]}`. Generic bounded tool selection: `POST /api/research` with `{"goal":"Compare bulk conductors between 600 K and 1100 K","row_ids":[1,2,3]}`. The same route supports single-temperature screening and `Inspect scientific evidence row 1`.

The **Research Agent execution** panel runs the exact Phase 2.6 screening, Huang interval and humidity/lifetime questions. Every result shows the selected tool, validated arguments, evidence verdict and deterministic grounded explanation, with JSON export. Unknown additions still abstain. `Around` is a disclosed nominal point; the named Huang demo means rows 1–3. To run current acceptance without any provider call:

```sh
uv run --offline --no-sync python scripts/accept_real_agent.py
uv run --offline --no-sync python scripts/validate_v2.py --browser --phase26
uv run --offline --no-sync python scripts/validate_v2.py --browser --phase261
uv run --offline --no-sync python scripts/validate_v2.py --browser --phase262
```

The second command records separate Phase 2.6 validation logs. Real acceptance requires usable `OPENAI_API_KEY` / `OXYPROOF_LLM_MODEL` configuration and explicit paid-use authorization; the default runner cannot trigger billable requests merely because credentials exist. See the Agent acceptance document before using its live flags.

For frontend editing: run the API plus `npm run dev --prefix frontend` in a second terminal (Vite proxies `/api` to loopback:8000). Production serves built assets from the API origin. No external fonts or chart service are used.

## Scientific contract and source rights

```
sigma(T) = A/T * exp(-Ea/(k_B*T))
Ea: meV -> eV; A: K S/cm; T: K; output: S/cm
```

This is the **verified convention of this curated dataset**, not a universal claim about all transport prefactors. Source DOI **10.5281/zenodo.18947543**; original CSV SHA-256:

```
8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34
```

The full file has 483 rows / 34 columns / 84 source DOIs; row means a reported composition/condition, not necessarily a unique composition (452 distinct formula strings). The dataset is **CC BY 4.0**. Attribution: Jang, Seong-Hoon; Kiyohara, Shin; Takamura, Hitoshi; Kumagai, Yu (2026), *Charting the Landscape of Oxygen Ion Conductors: A 60-Year Dataset*, Zenodo. Article rights are separately CC BY-NC-ND 4.0; no article text/figures are redistributed. The bundled subset preserves original field strings and maps to source rows in `backend/app/data/fixtures/manifest.json`.

Missing crossover metadata abstains, even where values look like sentinel placeholders. Unknown conductivity type is not coerced. Even within source groups, atmosphere, preparation and density are missing, so comparisons require review. Fit-derived conductivity is not a new measurement; no confidence intervals, phase-stability guarantees, novel-material discovery or autonomous experiments are claimed.

[Sources/schema](docs/SOURCES.md) · [Science assumptions/reference values](docs/SCIENCE_ASSUMPTIONS.md) · [Decisions](docs/DECISIONS.md) · [Competition evidence](docs/COMPETITION_RULES.md).

## Optional real LLM

DeepSeek uses explicit `OXYPROOF_LLM_PROVIDER=deepseek`, `OXYPROOF_LLM_MODEL=deepseek-flash` and `DEEPSEEK_API_KEY`, through the official `/responses` endpoint. Its three real A/B/C calls passed; no additional request is allowed in this completed sprint. The fixed durable budget prevents replacement processes from bypassing the cap. The Research Agent panel can load/replay these genuine captured traces without credentials or new inference, with `RECORDED_TRACE_REPLAY` labels. See the [acceptance report](docs/DEEPSEEK_LIVE_ACCEPTANCE.md) for exact calls, schema decisions and limits.

Local provider selection is explicit: `OXYPROOF_LLM_PROVIDER=ollama`, `OXYPROOF_LLM_MODEL=phi4-mini:latest`, `OXYPROOF_OLLAMA_BASE_URL=http://127.0.0.1:11434`. No OpenAI key is needed, and there is no cloud fallback. Native tool acceptance currently failed; follow the [Ollama report](docs/OLLAMA_REAL_AGENT_ACCEPTANCE.md) before any further inference. Omitted provider preserves the separate OpenAI configuration below.

The [OpenAI Responses function-calling adapter](https://developers.openai.com/api/docs/guides/function-calling) permits exactly one allowlisted typed plan: `screen_published_records`, `analyze_temperature_interval` or `inspect_scientific_evidence`. An explicit model, 25-second transport timeout, bounded output and no retries are enforced. The independent grammar verifies tool intent and field completeness; a model cannot broaden accepted constraints or introduce code/URLs. Only the goal text is sent. All scientific values, explanations and citations come from deterministic validated outputs, never provider prose.

For the separate OpenAI adapter, set `OXYPROOF_LLM_PROVIDER=openai`, `OPENAI_API_KEY` and `OXYPROOF_LLM_MODEL` in your own environment, then select `REAL_LLM` only with appropriate paid-use authorization. `.env.example` contains no secret; ignored `.env` may be passed explicitly using uvicorn `--env-file .env`. API failures are `UNAVAILABLE`, never silently substituted offline. Provider transport unit tests are mocked contracts; genuine DeepSeek evidence is stored separately. No OpenAI call was made in this sprint.

## Repository and submission

`backend/app/`: ingest, science, bounded planner, API and report contracts. `frontend/`: React/TypeScript, component and real browser tests. `scripts/`: retrieval, references, demos, bootstrap and browser capture. `benchmarks/`: retained eight educational guards plus 49 hand-selected v2 scientific-integrity cases, not a representative accuracy claim. `artifacts/`: generated audits and measured evidence; regenerate after calculation-code changes to refresh fingerprints. Original code is [MIT](LICENSE); scientific data and dependency rights are [separate](THIRD_PARTY_NOTICES.md).

Public 2026 deadline: **October 23, 2026 at 13:00 NZDT** per [2026 agenda](https://llmhackathon.github.io/agenda/), checked October 20. Final submission mechanism, registration and pre-event-work eligibility need human/Slack confirmation. The historical submission page is not the 2026 authority. [Submission checklist](docs/SUBMISSION_CHECKLIST.md) · [write-up draft](docs/ONE_PAGE_DRAFT.md).

At Phase 2.6 entry on October 21, local `main` was clean at `ff17b2b02e578101952143db8541c06d84ba3ea8`; earlier handovers/manifests describe their historical snapshots. Current Agent changes remain local; this sprint performs no commit, push, deployment, upload or submission. [Agent acceptance](docs/REAL_AGENT_ACCEPTANCE.md) · [prior release gate](docs/RELEASE_GATE.md) · [scientific acceptance](docs/SCIENTIFIC_ACCEPTANCE.md) · [one-page owner review copy](docs/FINAL_SUBMISSION_COPY.md).
