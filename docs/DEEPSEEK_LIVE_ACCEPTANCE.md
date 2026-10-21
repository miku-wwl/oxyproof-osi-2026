# Phase 2.6.2 - genuine DeepSeek scientific Agent acceptance

Executed **October 21, 2026 NZDT**, starting from clean `main` at `66919b8202c6289adb7301f3e7c530ff16c9d0c6`. **All three real DeepSeek scenarios passed independent scientific acceptance.** There were exactly **3 billable HTTP model requests, 3 HTTP 200 responses, 3 accepted native function calls, 3 scientific acceptance passes**, no retries or extra generation. The three-request sprint budget is exhausted and remains durably enforced across processes.

```text
DEEPSEEK_KEY_STATUS=PRESENT
DEEPSEEK_PROVIDER_STATUS=PASS
DEEPSEEK_MODEL=deepseek-flash
REAL_PROVIDER_REQUESTS_ATTEMPTED=3
REAL_PROVIDER_REQUESTS_SUCCEEDED=3
REAL_LLM_STATUS=VERIFIED
LIVE_SCREENING_STATUS=PASS
LIVE_TEMPERATURE_STATUS=PASS
LIVE_CONSTRAINT_REFUSAL_STATUS=PASS
AGENT_TRACE_STATUS=PASS
SCIENTIFIC_INTEGRITY_STATUS=PASS
BACKEND_TEST_STATUS=PASS
FRONTEND_TEST_STATUS=PASS
BROWSER_E2E_STATUS=PASS
BENCHMARK_STATUS=PASS
SCIENTIFIC_SOFTWARE_READINESS=GO
REAL_AGENT_READINESS=GO
SUBMISSION_READINESS=PARTIAL
SUBMISSION_STATUS=NOT_SUBMITTED
SPRINT_STATUS=PASS
EVENT_RULES_STATUS=PARTIAL
SCIENCE_DATA_STATUS=VERIFIED_REAL
OFFLINE_DEMO_STATUS=PASS
TEST_STATUS=PASS
```

GO means the demonstrated bounded research workflows and recorded judge demo are verified. It is not a material-performance guarantee, general model-accuracy claim, permission for additional paid requests or competition submission approval.

## Actual provider evidence

Official endpoint: **https://api.deepseek.com/responses**. Requested and returned model string: **deepseek-flash**. No other provider was invoked; no `/models`, connectivity ping or paid discovery call was made. The model alias was returned by the provider; underlying weights/version are not independently pinned or verified.

| Scenario | UTC start on October 21 | Actual selected tool | Wall seconds | Input / output / cached-input tokens | HTTP / independent result |
| --- | --- | --- | ---: | --- | --- |
| A | 05:02:58.527310 | `screen_published_records` | 1.109 | 1143 / 125 / 0 | 200 / PASS |
| B | 05:02:59.716012 | `analyze_temperature_interval` | 1.282 | 1146 / 135 / 896 | 200 / PASS |
| C | 05:03:01.128921 | `screen_published_records`, validation-only abstention | 1.140 | 1142 / 137 / 896 | 200 / PASS |

These are three sequential transport/parse measurements, not a representative latency benchmark or full UI latency. Totals: **3431 input + 397 output = 3828 tokens**, with **1792 cached input tokens** reported. Cached input is a subset of input; no monetary charge is inferred from these counters.

Genuine provider Response IDs:

- A: `19c61523-1de3-4224-bb62-d27c3b5e9855`
- B: `8555b7b9-84f2-4553-b7ec-0041482bc9aa`
- C: `36ab33a0-d258-4190-a5d4-4d867fd4fe0f`

Application `local_invocation_id` UUIDs are separately labelled. No ID was invented as a substitute for a provider ID. Provider reasoning text and free-form answers were not retained or used as scientific evidence. Raw tool arguments are bounded/redacted; C reported two unsupported constraints, whose paraphrased provider text was withheld by the existing redactor. Independent original-request coverage, not a guess about the redacted text, establishes the humidity/lifetime requirements.

`artifacts/deepseek_live_acceptance.json` contains source metadata, request/response identities, numeric usage, model-selected and independently expected tools, agreement, validated arguments, full scientific reports, audit verdicts and typed execution traces. The zero-cost preflight is retained separately in `artifacts/deepseek_preflight.json`.

## Scientific acceptance

**A:** The model returned 600 C, bulk, null class/formula filters and no unsupported constraint. The runner explicitly supplied evaluation rows **1,2,3**; this is a predefined evaluation group, not autonomous material discovery. Independent validation approved nominal **873.15 K**. The engine computed conditional order **3 > 2 > 1** using original source parameters and S/cm units. Rows 1/2 use HT, row 3 uses LT below T*=874.9335546 K and retains its near-transition warning. Source rows, raw strings, DOI and units were checked against a separate Decimal reference.

**B:** The model selected the interval tool with **700–1000 K**, bulk and rows **1,2,3** for the explicit named Huang group. Independent parsing and source-group checks agreed. Deterministic results: **700 K: 1 > 2 > 3; 1000 K: 3 > 2 > 1**. Independent 80-digit Decimal calculations verify analytic crossings **776.407425051 / 817.909825368 / 854.261466340 K**, all six endpoint conductivities and both-side ordering checks. The explanation uses curated Ea/EaHT and prefactor ratios; published T* regime boundaries are distinct from continuous analytical roots. No crossover is claimed experimentally measured, and uncertainty bounds are unavailable.

**C:** A genuine model request occurred before scientific constraint auditing. The model returned the screening function with two unsupported flags. Independent coverage retained **10% humidity** and **10,000 operating hours**. The typed result is **ABSTAINED / UNVERIFIED_CONSTRAINTS**, with **zero candidates, empty validated execution arguments and no executed scientific calculation tool**. Refusal origin is `BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR`. Missing exposure/durability measurements are proposed, never reported as completed experiments. The existing workflow already obtains a bounded plan before auditing, so no bypass or extra planning route was needed.

## API compatibility and safety decisions

Official documentation directly accessed **October 21, 2026**: [Responses guide](https://api-docs.deepseek.com/guides/responses_api/) and [create-response reference](https://api-docs.deepseek.com/api/create-response/). The normal `/responses` route supports function tools and `tool_choice=required`; `reasoning.effort=none` disables thinking. Parallel/max-tool limits are ignored, so exactly-one-call enforcement is local. Stateless requests send no prior response or stored conversation.

The adapter sends three function tools with basic JSON Schema: types, nullable alternatives, enums, objects, arrays, required fields and no additional properties. It removes titles/defaults and provider-side length/item/numeric bounds, and makes object properties explicitly required. No beta endpoint or assumed provider strict mode is used. **All original Pydantic bounds, extra-field rejection, units, row-ID validation and independent scientific constraints remain mandatory locally.** Tests demonstrate rejection of invalid units, invented source fields, missing prerequisites and overlong values.

The existing Responses byte-bounded single-attempt HTTP transport is reused. DeepSeek uses a **60-second read / 5-second connect timeout, 1200 output-token cap, non-streaming, temperature 0**, no SDK, default HTTPX transport retries=0, no redirects and no inherited proxy configuration. Only the question, schema, policy and class vocabulary are sent, never the full dataset. Server-side web search, code, custom tools and ordinary message JSON are rejected as scientific tool execution.

Explicit provider selection is `OXYPROOF_LLM_PROVIDER=deepseek`, `OXYPROOF_LLM_MODEL=deepseek-flash`, with `DEEPSEEK_API_KEY`. The CLI can securely read the Windows User-scoped key into its own process if absent from inherited environment; no permanent Windows setting is modified. Only PRESENT/MISSING is reported. OpenAI remains the omitted-provider backward-compatible default, and the existing Ollama adapter/failure evidence remain intact. There is no provider fallback.

The fixed ignored `.local/deepseek-phase262-budget.json` is claimed under an exclusive file lock **before each HTTP attempt**, including failures. The fourth request is blocked across process restarts; corrupt/locked state fails closed. A systemic API/transport/envelope failure durably halts the sprint. The runner refuses a replacement live run if evidence or spent budget exists. No ledger was reset to get more requests.

Normal regression removes provider credentials/configuration, disables cloud access, and isolates the browser server. Pytest forbids the actual HTTP network transport while allowing explicitly synthetic transports. The presence of the owner's key cannot activate ordinary regression inference. Provider/schema/timeout tests are mocks; they do not populate genuine live acceptance.

## Validation before and after paid calls

Before billing, the zero-cost preflight passed all 12 structural/configuration/coverage/science checks and full 16-stage regression: **246 backend / 11 component / 18 Chromium** tests, benchmark **49/49**, original offline cases and independent references. No paid ping was used.

After capture, a minimal trace/replay refinement was made and the complete regression rerun:

| Final check | Actual result |
| --- | --- |
| Backend pytest | **255 passed**, 0 failed/skipped, 1 existing Starlette/httpx deprecation warning |
| New DeepSeek transport/budget contracts | **34**, within the backend total; synthetic transport only |
| Recorded evidence/replay checks | **9**, within the backend total; archived real science checked independently, no inference |
| Existing Ollama contracts | **37 preserved**, within the backend total |
| Frontend component contracts | **12 passed**; provider identity examples are synthetic |
| TypeScript/Vite build, ESLint, Ruff check/format, dependency lock | PASS |
| Genuine Chromium | **21 passed**, 0 skipped/unexpected/flaky; includes three explicitly recorded DeepSeek replays |
| Frozen scientific benchmark | **49/49**, targeted cases, not representative accuracy |
| Original eight guards | Audited **8/8**, deliberately unsafe baseline **1/8** |
| Original published-data demos / offline Agent scenes | **5/5 / 3/3 PASS** |
| Independent science | **3 roots, 6 endpoint values, 6 side checks PASS**, 80 Decimal digits |

Exact comprehensive command:

```powershell
uv run --offline --no-sync python scripts/validate_v2.py --browser --phase262
```

It makes zero fresh model requests. Commands, stdout/stderr and durations are in `artifacts/deepseek_regression.json`; logs are under `.local/validation-deepseek/`. The three new browser tests use the real Python API and archived genuine provider output, verify replay labels/export and assert zero planning POSTs. They are not fresh browser-driven model calls. Screenshots are `artifacts/browser/deepseek-recorded-{a,b,c}.png`.

The fresh handover service is **http://127.0.0.1:8000**, PID **37268**, deliberately started without provider keys and with cloud disabled. Its configuration health can therefore say NOT_CONFIGURED even though the separately captured DeepSeek acceptance is VERIFIED. A separate current HTTP check passed **6/6**: health, offline A/B/C, fixed-archive replay and an explicit fresh-REAL_LLM request returning **503 CLOUD_DISABLED** before any provider transport. The budget ledger was byte-unchanged at 3 attempts (`artifacts/deepseek_http_smoke.json`). This checks failure isolation without consuming another paid request. The old owned service was replaced only after its PID/command matched; permanent Windows/Ollama settings were not touched.

## Trace correction and evidence preservation

The original live capture is preserved **byte-for-byte** in `artifacts/deepseek_live_capture_original.json`. Its capture-time backend fingerprint is **4213a7a0ae000488023e16d812e8ed340e320a65ba6c335804fc218991c272cd**.

After the successful run, review found that provider planning metadata retained an initial `executed_scientific_tool=null` placeholder for A/B, while the authoritative execution trace correctly named the tools and contained independently verified results. The workflow now updates that application field after auditing. The current acceptance artifact copies it from the already captured trace, and records the original capture SHA-256 and exact normalization rationale. **Provider IDs, token usage, model-selected arguments, scientific values and request count did not change.** No model call was repeated. The replay and final source fingerprint are therefore later than the capture; the math implementation, request grammar, dataset and frozen references remain unchanged and were revalidated.

Temporary local verification issues were limited to formatting findings resolved before billing and premature log-file reads while validation was still running. The final commands pass. **No live provider/scenario failed.** The retained Starlette warning and Playwright color-environment notices are disclosed, not hidden.

## Reproduction, demo and release limits

The actual authorized live command was:

```powershell
uv run --offline --no-sync python scripts/accept_deepseek_agent.py --live --authorize-paid-calls
```

It exited 0 with `REAL_LLM_STATUS=VERIFIED requests=3 succeeded=3`. **Do not rerun it in this sprint.** All three requests are spent, and a new process cannot bypass the durable cap. The no-flag form is a zero-cost preflight; after this completed run it reports the spent budget rather than resetting it. A new paid evaluation requires separate owner authorization and a separately reviewed phase/budget change.

Use the existing offline dashboard plus explicit archived evidence playback for judges; see [demo instructions](DEEPSEEK_AGENT_DEMO.md). The read-only `GET /api/research/recorded-deepseek` loads one fixed, size-bounded, schema/trace-checked artifact. The UI/export say `RECORDED_TRACE_REPLAY` and `fresh_model_request=false`, show actual captured provider IDs, and never represent playback as fresh inference. Missing/partial evidence refuses replay. No video was recorded or edited this sprint.

Scientific provenance remains the verified [Jang dataset DOI 10.5281/zenodo.18947543](https://doi.org/10.5281/zenodo.18947543), original CSV SHA-256 **8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34**, 483 records / 34 columns / 84 source DOIs, CC BY 4.0. The original 24-row fixture and independent references are preserved. Source pages were originally verified October 20; this sprint verifies cached bytes and calculations, not new source measurements. [Article](https://www.nature.com/articles/s41597-026-07100-x), [scientific acceptance](SCIENTIFIC_ACCEPTANCE.md), [source/rights record](SOURCES.md). Article rights are separate; no article text/figures were redistributed.

Sigma uses `A/T * exp(-Ea/(k_B*T))`, Ea meV -> eV, A K S/cm, T K, output S/cm. Atmosphere, preparation, density, fit uncertainty, humidity/lifetime and original-paper experimental conditions remain limited/unverified. Exact T* is withheld; the 5 K neighborhood is an engineering heuristic, not uncertainty. Three bounded successful questions do not establish general language understanding or statistical model reliability. The third allowlisted evidence-inspection tool has offline/mock contracts, not a separate paid acceptance call this sprint.

All work remains local and unstaged; exact changed paths/hashes, HEAD, protected assets and security-scan scope are in `artifacts/deepseek_change_manifest.json`. No commit, push, tag, deploy, upload, registration, social post or competition submission occurred. Original video/PDF are hash-preserved; no additional Ollama/OpenAI/other-provider inference occurred. Registration, latest Slack submission rules and eligibility of October 20 pre-event development remain human gates.
