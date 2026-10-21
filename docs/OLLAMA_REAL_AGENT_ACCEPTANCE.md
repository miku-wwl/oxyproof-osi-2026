# Phase 2.6.1 - local Ollama acceptance

Executed October 21, 2026 NZDT, from clean `main` at `3a470d21f5a610beefe92bb3d81cd2dfaa14862f`. This report supersedes the Phase 2.6 zero-call status, while preserving its historical evidence.

**The native real-Agent objective failed.** The provider integration is implemented and fails closed. Genuine CPU inference returned HTTP 200 three times, but all three responses contained **zero native tool calls**. No local-model scientific tool execution, successful scientific plan, candidate recommendation or provider Response ID was fabricated. No cloud provider was called.

```text
OLLAMA_SERVER_STATUS=READY
OLLAMA_MODEL_STATUS=READY
OLLAMA_MODEL=phi4-mini:latest
OLLAMA_TOOL_CALLING_STATUS=FAIL
LOCAL_LLM_STATUS=FAILED
LOCAL_SCREENING_STATUS=FAIL
LOCAL_TEMPERATURE_STATUS=NOT_RUN
LOCAL_CONSTRAINT_REFUSAL_STATUS=NOT_RUN
REAL_MODEL_REQUESTS_ATTEMPTED=3
REAL_MODEL_REQUESTS_SUCCEEDED=0
AGENT_TRACE_STATUS=PARTIAL
SCIENTIFIC_INTEGRITY_STATUS=PASS
BACKEND_TEST_STATUS=PASS
FRONTEND_TEST_STATUS=PASS
BROWSER_E2E_STATUS=PASS
BENCHMARK_STATUS=PASS
RELEASE_READINESS=NO_GO
SUBMISSION_STATUS=NOT_SUBMITTED
SPRINT_STATUS=PARTIAL
EVENT_RULES_STATUS=PARTIAL
SCIENCE_DATA_STATUS=VERIFIED_REAL
REAL_LLM_STATUS=FAILED
OFFLINE_DEMO_STATUS=PASS
TEST_STATUS=PASS
SUBMISSION_READINESS=PARTIAL
```

`REQUESTS_SUCCEEDED` here means an accepted native structured plan, **not HTTP success**. There were 3 completed HTTP/inference responses, 0 accepted native plans, 0 live scientific acceptance passes. AGENT_TRACE_STATUS is PARTIAL because local invocation/failure evidence and tested trace contracts exist, but no successful native scientific execution trace exists. NO_GO applies to release claims of a verified real local Agent; the offline scientific dashboard remains usable.

## Live environment and scope

- Ollama CLI/API version **0.35.1**. `ollama list`, `ollama ps`, `/api/version`, `/api/tags`, `/api/ps` directly inspected; no inference was used merely to prove preflight.
- Installed model **phi4-mini:latest**, digest `78fad5d182a7c33065e153a5f8ba210754207ba9d91973f57dffa7f487363753`, 3.8B Q4_K_M. Metadata advertises `completion` and `tools`; this is not evidence of successful tool calling.
- Before/after `/api/ps`: 4096-token context, model allocation **3,094,704,290 bytes**, `size_vram=0`; CLI **100% CPU / Forever**. This describes backend selection/residency, not constant whole-system CPU utilization. One post-inference Windows observation recorded llama-server working set near 2.98 GB; this is observed memory, not a peak profile.
- Model listing requires [Ollama 0.5.13 or later](https://ollama.com/library/phi4-mini); installed 0.35.1 exceeds that requirement. The server accepts tools and generates responses, but actual output still failed. Exact model/runtime/prompt cause is unresolved; do not claim the feature is universally unsupported.
- No startup, login, user environment or model files were changed. No model was downloaded, replaced or unloaded. Reboot persistence remains untested.

## Actual requests and failures

| Request | Role | Wall seconds | Input / output tokens | Prompt / generation seconds | Native tool calls | Result |
| --- | --- | ---: | --- | --- | ---: | --- |
| 1 | Primary A, all three allowlisted functions | 39.813 | 744 / 298 | 8.217489 / 31.420119 | 0 | FAIL: `NATIVE_TOOL_CALL_REQUIRED` |
| 2 | Diagnostic 1: A with explicit native-format cue | 15.687 | 765 / 90 | 8.118345 / 7.374309 | 0 | FAIL: same error |
| 3 | Diagnostic 2: minimal evidence-row tool | 2.110 | 112 / 11 | 1.292717 / 0.692445 | 0 | FAIL: ordinary text, no scientific execution |

Model load durations were 0.011249 / 0.006299 / 0.006792 seconds. All requests were sequential, temperature 0, context 4096, `keep_alive=-1`, non-streaming, 180-second HTTP read timeout, 5-second connection timeout, no retries. Primary/diagnostic 1 output cap was 512 tokens; diagnostic 2 used 256. These are individual warm-resident measurements with different prompts, not a representative performance benchmark or a cold-start test.

Diagnostic 2's untrusted content was `{k: 1, unsupported_constraints: []}`. It was retained as failure evidence, never parsed into a scientific plan or shown as scientific evidence. The runner's systemic-error stop left **B and C NOT_RUN**. After one primary and both authorized diagnostic calls failed, no additional inference was attempted. This follows the owner's instruction to investigate systemic failures before continuing and to avoid speculative retries. No second primary A run was substituted for the original failure. No constrained-JSON fallback was tested or labelled native calling.

Primary A has no model-selected function/arguments, validated arguments, executed scientific tool or result. The deterministic expectation was screening; agreement is unavailable because no function was selected. B's ranking and C's refusal are verified **offline and in mocked contracts only**, not by this model. All local invocation UUIDs are explicitly application-generated; `response_id` is null.

## Engineering changes

`backend/app/agents/ollama.py` implements native `/api/chat` normalization into the existing strict Pydantic tool contracts. Configuration explicitly selects `ollama` or `openai`; omitted provider preserves OpenAI compatibility. Ollama needs no key. The local adapter permits only literal `http://127.0.0.1:11434` and installed `phi4-mini:latest`, disables proxy inheritance/redirects/retries, limits response bytes to 64 KiB and transmits only the question, tool schemas and class vocabulary. It never transmits the 483-row dataset, calculates physics, executes code or fetches model-proposed URLs.

Exactly one allowlisted native call and all typed fields are required. Missing/multiple tools, malformed JSON, wrong fields/units/rows/model identity, invented source fields and provider errors fail closed. Tool-specific arguments can be native objects or JSON strings, but ordinary message JSON is never promoted into a tool call. Safe telemetry preserves numeric counts/durations, actual model identity and redacted raw arguments. Untrusted provider prose/unknown argument values never become scientific evidence.

Shared traces now distinguish model-selected tool, deterministic expectation, agreement, executed bounded tool and refusal origin. Fixed tool endpoints retain `FIXED_ENDPOINT`, without claiming model-discovered action. Local identity is accepted without manufacturing an OpenAI-style response ID. Offline traces still forbid provider identity. The Agent panel conditionally displays `REAL_LLM — Ollama Local — phi4-mini:latest` **only after an actual accepted execution**, and otherwise shows UNAVAILABLE with no offline substitution. That successful local label has component-contract coverage, not successful live-model UI evidence. Browser transport waits 190 seconds so CPU inference can finish before the 180-second provider timeout.

`scripts/accept_real_agent.py --local-live` explicitly sets the local provider/model/endpoint and runs at most three primary cases sequentially, stopping on systemic provider failures. Normal acceptance and browser regressions never activate local inference. Paid OpenAI flags remain separate and cannot activate Ollama. Tests clear inherited configuration; browser launcher and Playwright server independently force unconfigured OpenAI regression mode.

## Reproduce and inspect

Safe regression, with **zero inference calls**:

```powershell
uv run --offline --no-sync python scripts/validate_v2.py --browser --phase261
uv run --offline --no-sync python scripts/accept_real_agent.py
uv run --offline --no-sync python scripts/verify_final_science.py
```

The live command implemented and actually executed was:

```powershell
uv run --offline --no-sync python scripts/accept_real_agent.py --local-live
```

It exited 1 with `LOCAL_LLM_STATUS=FAILED`, after A failed and the systemic stop withheld B/C. Do not rerun live or diagnostic commands within this completed sprint: the two diagnostic requests are exhausted. A new investigation needs a new owner-approved inference budget. Recorded diagnostic requests, timestamps, original code fingerprints and responses are preserved in `artifacts/ollama_diagnostic_1.json` and `ollama_diagnostic_2.json`; no live outputs are reconstructed from mocks.

To configure a future interactive process (selecting REAL_LLM and clicking Run would make another inference request):

```powershell
$env:OXYPROOF_LLM_PROVIDER='ollama'
$env:OXYPROOF_LLM_MODEL='phi4-mini:latest'
$env:OXYPROOF_OLLAMA_BASE_URL='http://127.0.0.1:11434'
uv run --offline --no-sync python scripts/start.py --offline
```

No permanent environment setting or credential file is required. A default offline request remains deterministic even with this provider configured.

## Current regression and scientific evidence

Final 16-stage command above records commands, stdout/stderr and elapsed times in `artifacts/ollama_regression.json`; raw logs are under `.local/validation-ollama/`.

The fresh handover service is on **http://127.0.0.1:8000**, PID 57288, with Ollama selected only in that process's environment. Health reports `CONFIGURED_NOT_VERIFIED`, never a successful acceptance status. Three additional actual HTTP requests used explicitly offline mode and passed independent A/B/C assertions while this provider was configured (`artifacts/ollama_http_offline.json`); they made zero inference requests. The previously owned stale application service was replaced after checking its exact PID/command. No other runtime or permanent Ollama setting was altered.

- Backend **212 passed**, 0 failed/skipped, one existing Starlette/httpx deprecation warning. Includes **37** local adapter/failure/runner/label-integrity contract cases; mocked transports are not live evidence.
- Frontend **11 passed**; synthetic provider identity is explicitly labelled as a component contract. TypeScript/Vite build and ESLint PASS.
- Genuine Chromium **18 passed**, 0 skipped/unexpected/flaky. Science uses the real Python API; provider configuration is intentionally isolated and no model inference occurs. Existing explicit failure injection remains labelled.
- Ruff check/format and locked dependency check PASS. Frozen benchmark **49/49**, original eight guards **8/8** versus intentionally unsafe baseline **1/8**; no representative accuracy claim.
- Original published-data demos **5/5** and Agent offline A/B/C **3/3** PASS. Independent 80-digit Decimal verification: **3 roots, 6 endpoint values, 6 side checks PASS**.

The full pinned dataset remains **483 rows, 34 columns, 84 source DOIs**, SHA-256 `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34`; the original 24-row CC BY 4.0 fixture, math implementation, frozen benchmark/reference and dependency locks are unchanged. [Dataset](https://doi.org/10.5281/zenodo.18947543), [article](https://www.nature.com/articles/s41597-026-07100-x), [existing scientific acceptance](SCIENTIFIC_ACCEPTANCE.md). Source metadata and cached bytes were locally verified this sprint; source/event pages were not freshly revalidated for this bounded provider task.

Sigma is `A/T * exp(-Ea/(k_B*T))`, with CSV Ea meV converted to eV, A K S/cm, T K, output S/cm. Offline Huang rows 1/2/3 rank 1>2>3 at 700 K and 3>2>1 at 1000 K; analytic crossings are 776.407425 / 817.909825 / 854.261466 K. At nominal 600 C = 873.15 K, rows 1/2 use HT but row 3 uses LT and retains its near-transition warning. Exact T* is withheld, 5 K is an engineering heuristic, and source conditions/fit uncertainty/humidity/lifetime remain unverified. None of those values came from model arithmetic or constitutes experimental confirmation.

Temporary verification failures are disclosed: duplicate offline wording initially broke one component query; a subsequently clarified REAL_LLM selection badge broke one legacy offline-label assertion. Both presentation issues were corrected; final regression evidence supersedes the intermediate failed runs. The real model failures remain failures. The accepted 204-second video and one-page PDF were hash-preserved and no new real-model recording was made.

## Release boundary and next actions

All changes remain local and unstaged; exact paths/hashes and Git state are in `artifacts/ollama_change_manifest.json`. No commit, push, deployment, publication, registration, paid call or submission occurred. No Kubernetes, framework, dataset, training or unrelated Windows change was introduced. OpenAI behavior has mock regression coverage but no cloud call this sprint.

1. Approve a separate bounded investigation into Phi4-mini native-output formatting/runtime compatibility; do not claim success from model metadata.
2. Require all A/B/C genuine plans and independent scientific assertions before any verified real-Agent release or recording.
3. Use the reliable offline Temperature Decision Explorer for the current judge demonstration.
4. Confirm registration, current Slack submission instructions and eligibility of October 20 pre-event development.
5. Review evidence and authorize any future Git publication/submission separately.

Official technical sources directly accessed October 21: [native chat API](https://docs.ollama.com/api/chat), [tool calling](https://docs.ollama.com/capabilities/tool-calling), [Ollama API repository reference](https://github.com/ollama/ollama/blob/main/docs/api.md), [Phi4-mini listing](https://ollama.com/library/phi4-mini), [Microsoft model card input formats](https://huggingface.co/microsoft/Phi-4-mini-instruct#input-formats). These describe intended APIs/formats, not a passing acceptance result for this host.
