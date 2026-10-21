# Phase 2.5 final acceptance handover - 2026-10-20 NZDT

```text
PHASE2_5_STATUS=PARTIAL
SCIENCE_SOURCE_STATUS=PARTIAL
SCIENTIFIC_CLAIMS_STATUS=PASS
CROSSOVER_VALIDATION_STATUS=PASS
CONSTRAINT_SAFETY_STATUS=PASS
REAL_LLM_STATUS=NOT_CONFIGURED
FULL_DATASET_STATUS=VERIFIED
BACKEND_TEST_STATUS=PASS
FRONTEND_TEST_STATUS=PASS
BROWSER_E2E_STATUS=PASS
BENCHMARK_STATUS=PASS
VIDEO_ACCEPTANCE_STATUS=PASS
ONE_PAGE_SUBMISSION_STATUS=READY
LICENSE_STATUS=PASS
ELIGIBILITY_STATUS=UNVERIFIED
RELEASE_CANDIDATE_STATUS=CONDITIONAL_GO
SUBMISSION_STATUS=NOT_SUBMITTED
SPRINT_STATUS=PARTIAL
EVENT_RULES_STATUS=PARTIAL
SCIENCE_DATA_STATUS=VERIFIED_REAL
OFFLINE_DEMO_STATUS=PASS
TEST_STATUS=PASS
SUBMISSION_READINESS=READY_FOR_HUMAN_ACTION
```

## 1. Executive review

**CONDITIONAL_GO / READY_FOR_OWNER_REVIEW.** The existing scientific workbench is a verified local release candidate with a qualified narrative, real-data numerical references, functioning React/API workflow and accepted media. This sprint did not rebuild the architecture. Overall PARTIAL reflects missing primary full methods, no configured live LLM and unresolved eligibility/submission/public-action gates. It is not a failed offline computation or a claim of successful competition submission.

## 2. Exact changes

- Added a persistent scientific uncertainty qualification to temperature reports/exports and a visible UI banner. Event headings/tooltips now use nearest-kelvin presentation; raw roots and sample coordinates remain available for reproducibility. Calculation algorithms and published parameters are unchanged.
- Extended regression coverage for long-term phase stability, absent/corrupt full data, typed data unavailability and provider HTTP failure. Added browser assertions for rounded display, qualification and precise export. Browser traces are retained for all acceptance flows.
- Added a separate 80-digit Decimal/SI reference script, checking three roots, six endpoint values, common regimes, both-side ordering and 40/80-digit arithmetic stability.
- Preserved original video bytes; captured and reviewed a separate updated video with rounded roots and an explicit uncertainty/confirmation caption. Enhanced media inspection with frame rate and tail extraction.
- Prepared final scientific evidence matrix, claim audit, validation, one-page copy/PDF, media review, release gates, configuration acceptance and file manifest. Added optional isolated PDF-rendering helper and runtime dependency license notices. Refreshed deterministic scientific artifacts to the current code fingerprint.
- Corrected current README/timeline statements using the actually observed existing commit/remote; historical handovers remain historical.

The exact path/status/size/hash list is `artifacts/release_candidate_manifest.json`; its file list is the definitive sprint diff against entry HEAD. Protected fixture/manifest, original eight-guard evaluator, frozen 49-case corpus, application locks, AGENTS and root project brief/prompt are unchanged. Nothing was staged or committed.

## 3. Scientific verification

`SCIENTIFIC_ACCEPTANCE.md` separates VERIFIED_FROM_PRIMARY_SOURCE, VERIFIED_FROM_CURATED_DATASET and NOT_VERIFIED. Dataset methodology/units and Zenodo v1 rights were directly fetched. The original publisher abstract and author institutional citation were inspected. Direct DOI/PDF retrieval returned HTTP 403; the web PDF route resolved to an abstract. **Original full methods/Table 3 were not inspected.**

The three row formulas, both parameter sets, bulk/type, two-probe AC, 600-1100 K and curated T* are verified from the pinned CSV. Independent roots are 776.407425051022..., 817.909825367825... and 854.261466339589... K, in LT/LT, HT/LT and HT/LT joint evidence respectively. Public presentation uses approximately 776, 818 and 854 K. At 700 K: 1 > 2 > 3; at 1000 K: 3 > 2 > 1. Source/raw parameters/reference equality/side orderings are in `artifacts/scientific_acceptance.json`.

Model: sigma=A/T*exp(-Ea/(k_B*T)); CSV meV converted to eV in production, independently to SI joules in reference; A K S/cm; T K; sigma S/cm. Production agreement tolerances are arithmetic checks, not scientific error bars. Curated T* is distinct from a continuous model crossing and is withheld exactly. Synthetic discontinuity/outside-evidence counterexamples remain labelled test-only.

## 4. Conditions and uncertainty

Same DOI/type/method/range permits a provisional conditional model comparison. Row-specific atmosphere, fabrication, density, porosity, microstructure and parameter/measurement uncertainties remain unverified. No humidity/cycling stability or experimental superiority is inferred. **Model-derived crossover temperatures; uncertainty bounds unavailable; experimental confirmation required.** The +/-5 K neighborhood and numeric tie tolerances remain engineering heuristics. Follow-up measurement advice is a deterministic proposal, not executed research.

## 5. Live-model acceptance

No OPENAI_API_KEY/OXYPROOF_LLM_MODEL pair or .env was found. `artifacts/real_llm_acceptance.json` records **NOT_CONFIGURED, 0 provider calls, no live traces**. No paid use was initiated. Mock strict-tool/provider tests verify contracts only. All scientific explanations and citations come from deterministic validated outputs; provider prose is ignored.

The exact free-prose acceptance prompts A/B also exceed the current independent grammar and are rejected. Guided supported requests and explicit controls work; do not advertise arbitrary natural-language understanding. Scenario C retains humidity/long-term requirements and abstains. A future authorized live run must handle this limitation honestly; no model may bypass coverage to make a demo pass.

## 6. Actual results

Latest full validation: **145 backend tests passed, 0 skipped, 1 existing deprecation warning; 8 component tests passed; 14 Chromium tests passed, 0 skipped/unexpected/flaky; 49/49 targeted scientific integrity cases; 5/5 original offline demos; 6/6 real HTTP smoke checks plus an actual interval HTTP request; production build/ESLint/Ruff/lock checks PASS.** The optional PDF helper was subsequently linted/formatted with the full code directories: PASS, 45 files. A temporary helper closure lint issue was fixed, not hidden.

The benchmark is selected, partly synthetic and overlapping with tests. It is not general accuracy, statistical significance or a model-quality evaluation. Component/provider HTTP is mocked; browser/API calculations and downloaded JSON are real. One browser 503 injection is explicitly synthetic. Detailed commands/stdout/warnings are in `FINAL_VALIDATION.md` and `artifacts/final_validation.json`.

## 7. Reproduce and demonstrate

Prerequisites: Python 3.12+, uv, Node 22.12+ and npm. Run from the repository root:

```sh
python scripts/start.py
# After setup, no dependency sync, download or build:
python scripts/start.py --offline
uv run --offline --no-sync python scripts/validate_v2.py --browser
uv run --offline --no-sync python scripts/phase2_demo.py
uv run --offline --no-sync python scripts/verify_final_science.py
uv run --offline --no-sync python scripts/smoke.py
```

The owned final service is available at **http://127.0.0.1:8000** in this session. After stopping it, start again with the offline command. Do not start two servers on the same port or stop unrelated processes. A new ignored `.local/repro-venv` was created from the locked cached packages; the full-data demo passed there. Bootstrap also did a clean npm ci. This verifies fresh cached project environments on Windows, not a fresh operating system or POSIX.

Full data were freshly fetched: 483 records / 34 columns / 84 source DOIs / 452 formula strings; SHA-256 `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34`. CC BY 4.0 attributed. The 24-row fixture remains unchanged and visibly distinct; corrupt full data refuses fallback.

Demo: flagship preset -> 700 K -> 1000 K -> root and T* -> wrong-formula audit -> humidity request/refusal -> source evidence -> JSON export. Runtime is OFFLINE_DETERMINISTIC; all science uses the real API. Dataset/sources may be retrieved during setup, but normal analyses need no network.

## 8. Video and PDF

New accepted video: `.local/demo-phase25/oxyproof-phase2.webm`, **204.76s, 1440x1000, 25 fps, VP9/WebM, no audio**. Ten scenes plus near-end frame were actually inspected. Original `.local/demo/oxyproof-phase2.webm`, 204.4s, remains byte-for-byte unchanged. The original is historical and has less careful precision presentation. No upload or MP4 is claimed.

PDF: **`D:\workshop\oct\oxyproof-osi-2026\output\pdf\oxyproof-one-page-submission.pdf`**, exactly **1 A4 page**, verified by pypdf/pdfinfo and a rendered PNG inspection. Source is `FINAL_SUBMISSION_COPY.md`; optional rendering commands are in `FINAL_VALIDATION.md`. Poppler's Symbol-font warning had no visible defect. This is an owner-review copy, not submitted content.

## 9. Allowed / prohibited claims

Allowed: audited conditional interpretation of curated published fits; temperature-dependent model ranking reversal; typed abstention; source provenance/export; independently reproducible arithmetic; 49 targeted scientific integrity cases passed. Contribution is the integrated decision/evidence workflow, not the Arrhenius algebra or an assertion of scientific priority.

Prohibited: new synthesized/discovered material, measured crossover, experimentally confirmed superiority/device behavior/humidity stability, validated confidence intervals, general 100% scientific accuracy, autonomous experiments, live-model success or organizer eligibility. Full claim-to-test mapping is `JUDGE_CLAIMS_AUDIT.md`.

## 10. Organizer / eligibility questions

Public [2026 agenda](https://llmhackathon.github.io/agenda/) directly checked October 20: October 21-22 event; October 23 00:00 UTC = 13:00 NZDT deadline; social post with optional up-to-four-minute video/presentation and up-to-one-page write-up. The historical [submission page](https://llmhackathon.github.io/submission/) says September 12/two minutes and links a form; that conflict remains explicit. No attendee Slack was checked, registration confirmed or terms accepted.

Owner must confirm accepted registration/team, authenticated Slack latest rules, eligibility of development begun October 20, exact final fields/channel/form/tags, media rules, public URLs and successful submission acknowledgment. See `RELEASE_GATE.md` checklist.

## 11. Exact release artifacts

Required documents: `SCIENTIFIC_ACCEPTANCE.md`, `FINAL_VALIDATION.md`, `JUDGE_CLAIMS_AUDIT.md`, `FINAL_SUBMISSION_COPY.md`, `FINAL_DEMO_REVIEW.md`, `RELEASE_GATE.md` and this handover, all under `docs/`.

Required JSON: `artifacts/final_validation.json`, `artifacts/real_llm_acceptance.json`, `artifacts/release_candidate_manifest.json`. Additional evidence: `scientific_acceptance.json`, `primary_source_acceptance.json`, `final_demo_validation.json`, `pdf_acceptance.json`, `final_http_decision.json`, `license_inventory.json`, `repository_access_acceptance.json`; updated existing reports/benchmark/browser screenshots. Accepted PDF is under `output/pdf/`; large videos, browser binaries, traces, cached full CSV and environments remain ignored under `.local/`. No scientific evidence/assets were deleted for size.

## 12. Remaining blockers by severity

1. **P0 / human:** registration, latest Slack/form requirements, pre-event-work eligibility and explicit approval for public changes/uploads/submission. These prevent a submission-ready claim.
2. **P1 / optional live claim:** provide supported key/model configuration and explicit paid-use permission, then run at most the bounded three acceptance scenarios plus necessary diagnostics. Current exact A/B wording is also outside coverage.
3. **P1 / stronger science:** obtain legitimate full original methods/Table 3, verify row conditions and uncertainties, and plan actual measurements. Until then use conditional model claims only.
4. **P2:** owner full-video playback and final media-format preference; no functional offline blocker remains.

## 13. Git / hygiene

Entry working tree was clean on `main`, **HEAD `c9e72efa8f1a6bd77c80031c0e5208154393dc72`**. Read-only remote main SHA matched; unauthenticated GitHub REST confirmed the existing repository is public: **https://github.com/miku-wwl/oxyproof-osi-2026**. This sprint did not create that commit or push it. Final acceptance modifications are local and unstaged; manifest records exact current paths and hashes. Original SSH remote configuration is preserved. Full diff whitespace check passed; normal autocrlf advisory messages were not treated as failures or used to change global Git settings.

MIT original-code license, CC BY 4.0 fixture attribution, separate article rights and 30 Python / 271 npm dependency license evidence were checked. Runtime frontend notices are retained in `THIRD_PARTY_RUNTIME_LICENSES.txt`. Final bounded secret-pattern and trace scans are in the manifest, with their limits; no security certification is implied. Localhost URLs are explicitly local demo instructions, not deployment URLs.

## 14. Actions not performed / final decision

No commit, push, tag, release, publication, deployment, registration, organizer message, media upload, paid model call, cloud resource or competition submission was performed. Existing user files/history and original recording are preserved. **CONDITIONAL_GO for owner review of the qualified local slice; not unconditional release or competition submission.**

NEXT_OWNER_ACTIONS:
1. Confirm registration/team, latest Slack submission process and eligibility of October 20 work.
2. Review the accepted video, one-page PDF, scientific limitations and exact release manifest.
3. Explicitly authorize any commit/push/media publication and subsequent submission.
4. If live LLM evidence is desired, supply model configuration via environment and authorize bounded paid calls; retain current claims otherwise.
5. Obtain original full methods/conditions before strengthening scientific or experimental claims.
