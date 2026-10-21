# OxyProof — browser-operation video acceptance

SPRINT_STATUS=PARTIAL
BROWSER_OPERATION_VISIBILITY=PASS
FULLSCREEN_APPLICATION_PRESENTATION=PASS
SLIDER_INTERACTION=PASS
DEEPSEEK_REPLAY=PASS
JSON_EXPORT=PASS
IAB_SKILL_EXECUTION=PASS
MEDIA_TECHNICAL_VALIDATION=PASS
BROWSER_PLAYBACK_STATUS=PARTIAL
REAL_CURSOR_VISIBILITY=UNAVAILABLE
NATIVE_BROWSER_WINDOW_CHROME=UNAVAILABLE

**Overall acceptance is PARTIAL.** The IAB screenshot API does not capture the real system pointer or native address bar/window chrome. This is genuine webpage viewport footage. No cursor, pointer trail, click animation, UI result or scientific output was fabricated. The six named gates above concern the verified operations and application presentation; they do not waive the separate real-cursor requirement.

## Deliverables and presentation

Both MP4s are 03:15 (195.000 seconds), 1920×1080, H.264 High Level 4.0, yuv420p, 30 fps / 5,850 frames, TV range, faststart, with no audio. The clean edition has no narration subtitles. Both have only a brief final GitHub URL over the actual dashboard at 03:12–03:15. There is no opening title card, permanent title banner, editorial commentary rail or decorative frame. The native OxyProof navigation sidebar belongs to the actual application.

The clean video fills the canvas with the genuine webpage. Minimal caption strips are 84/1080 pixels high, leaving at least 92.22% unobscured application in the subtitled edition (the JSON viewer occupies the evidence-inspection scene). Source frames are 1921×1081, including unused capture-interface padding. The inspected full webpage rectangle is 1749×984 at [0,0,1749,984]; resizing to the output is approximately 1.098×. This is **not native 1080p or native 30-fps capture**. The same real operations and timing underlie both editions.

The SRT contains 25 short English action cues, not a verbatim transcript. The narration is 369 words, aligned to seven actual sections; owner voice recording is pending. Both supplied video masters are intentionally silent.

## IAB skill execution and source handling

The actual installed skill was read and executed: `C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md`. Its internal ID is `codex-iab-video-recording`; its display name is **IAB Browser Video**. These names identify the same installation.

The skill `capture_iab.mjs` recorded timestamped genuine captures concurrently with actual UI actions in the selected ChatGPT IAB (browser 2 / application tab 1). Its `render_iab.py` was run for the successful 8-second preflight and complete decode/visual inspection. The production renderer uses the verified source hashes and timestamps, preserving actual duration at 1× speed. It adds only padding removal, output scaling, minimal captions and the final supplied GitHub URL. No external browser, Windows desktop control, OBS or synthetic UI was used.

The previous explainer and original full-resolution frames were reviewed first. Fresh capture was necessary for the complete current selection → Analyze → slider → B/C replay → download → JSON-viewer chain. Previous media, raw captures, accepted PDF and submission copy are preserved. Private raw captures remain under `.local/browser-demo-capture/`; they are not bundled as public material.

Eight accepted takes are joined in original scene order, with necessary cuts between scenes and no speed-up. The original closing navigation take F included a transient loading frame and changed capture dimensions. It remains preserved but is excluded; F-ready shows the genuine ready dashboard after that navigation. The initial incorrect-coordinate preflight did not establish slider movement and was excluded; the successful native-drag preflight and the final three actual drags establish it.

| Take | Final interval | Actual acquisition fps | Maximum sample gap (s) | Frames used |
|---|---|---:|---:|---:|
| A1 | 00:00.000–00:12.000 | 12.302 | 0.259 | 147 |
| A2 | 00:12.000–00:35.000 | 12.165 | 0.274 | 279 |
| B | 00:35.000–01:15.000 | 12.447 | 0.316 | 498 |
| B-roots | 01:15.000–01:35.000 | 12.105 | 0.419 | 242 |
| C | 01:35.000–02:15.000 | 12.299 | 0.391 | 492 |
| D | 02:15.000–02:45.000 | 12.514 | 0.491 | 375 |
| E | 02:45.000–03:10.000 | 9.743 | 1.836 | 243 |
| F-ready | 03:10.000–03:15.000 | 6.564 | 0.322 | 32 |

The capture target was 15 fps; source acquisition varies with IAB latency. The largest 1.836-second gap occurs during E navigation to the JSON viewer. Repeated frames at 30-fps export preserve elapsed time and do not add motion detail.

## Timestamped actual operations

Times below are the recorded action request and completion mapped into the final video, rather than merely planned timings. Readability holds and resulting states are visible after completion. Source manifests and frame hashes are linked in `review/recording-provenance.json`.

| Take | Actual action | Requested | Completed |
|---|---|---:|---:|
| A1 | navigate-temperature-explorer | 00:02.059 | 00:02.926 |
| A1 | open-source-group-selector | 00:04.011 | 00:05.245 |
| A1 | select-published-Huang-group | 00:06.007 | 00:06.354 |
| A1 | open-actual-record-selection | 00:09.062 | 00:09.882 |
| A2 | clear-source-selection | 00:13.053 | 00:14.074 |
| A2 | select-source-row-1 | 00:15.022 | 00:15.909 |
| A2 | select-source-row-2 | 00:17.052 | 00:17.882 |
| A2 | select-source-row-3 | 00:19.020 | 00:19.771 |
| A2 | close-three-record-selector | 00:21.019 | 00:22.172 |
| A2 | enter-700K-lower-bound | 00:23.074 | 00:23.423 |
| A2 | enter-1000K-upper-bound | 00:25.025 | 00:25.345 |
| A2 | click-real-Analyze-interval | 00:28.069 | 00:29.221 |
| A2 | scroll-to-generated-curves | 00:32.052 | 00:33.130 |
| B | show-700K-order | 00:40.040 | 00:41.177 |
| B | actual-slider-drag-first-step | 00:47.058 | 00:48.466 |
| B | actual-slider-drag-second-step | 00:52.002 | 00:53.435 |
| B | actual-slider-drag-to-1000K | 00:57.019 | 00:58.441 |
| B | click-1000K-and-hold-ranking | 01:02.013 | 01:03.187 |
| B | return-700K-for-direct-comparison | 01:10.009 | 01:10.920 |
| B-roots | scroll-to-real-event-cards | 01:16.051 | 01:17.474 |
| B-roots | inspect-776K-model-event | 01:19.054 | 01:20.146 |
| B-roots | inspect-818K-model-event | 01:24.050 | 01:24.841 |
| B-roots | inspect-854K-model-event | 01:29.051 | 01:29.902 |
| B-roots | read-evidence-limitations | 01:32.072 | 01:33.252 |
| C | navigate-to-research-Agent | 01:36.057 | 01:37.115 |
| C | expand-recorded-DeepSeek-interface | 01:39.033 | 01:40.368 |
| C | click-load-recorded-traces | 01:43.004 | 01:44.143 |
| C | click-actual-Replay-B | 01:48.005 | 01:49.028 |
| C | show-provider-and-selected-tool | 01:53.013 | 01:54.394 |
| C | expand-actual-validated-arguments | 01:59.024 | 01:59.936 |
| C | expand-actual-scientific-result | 02:05.021 | 02:05.936 |
| C | show-independent-evidence-verdict | 02:10.043 | 02:11.279 |
| D | click-visible-Replay-C-control | 02:16.040 | 02:16.991 |
| D | show-original-humidity-and-lifetime-question | 02:18.055 | 02:19.397 |
| D | show-model-proposal-and-no-executed-tool | 02:26.040 | 02:26.883 |
| D | show-independent-constraint-audit | 02:34.063 | 02:35.295 |
| D | hold-grounded-insufficient-evidence-result | 02:39.026 | 02:40.011 |
| E | return-to-original-source-evidence | 02:46.045 | 02:47.119 |
| E | show-real-source-rows-and-parameters | 02:50.030 | 02:50.935 |
| E | click-Export-and-verify-real-downloaded-file | 02:57.044 | 02:58.136 |
| E | open-byte-identical-downloaded-JSON-in-IAB | 03:02.013 | 03:07.168 |
| F-ready | focus-ready-dashboard-heading | 03:11.019 | 03:12.182 |

The three final native IAB drags changed the real slider indices 0 → 31 → 60 → 92. At 700 K the visible order is 1 > 2 > 3; at 1000 K it is 3 > 2 > 1. The interaction proof contains observed bounds, actual drag coordinates and before/after values, not a drawn cursor. The approximate model crossings are displayed and read at 01:19–01:35.

Replay controls are visibly operated, including Load recorded DeepSeek traces, Replay B and Replay C. B shows `analyze_temperature_interval`, validated 700–1000 K / rows 1,2,3 and the independent audit. C shows the original humidity and 10,000-hour question, model proposal, `BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR`, no executed scientific tool and zero candidates.

The actual Export JSON click completed at 02:58.136. The real download is 141,505 bytes. The local viewer displays a byte-identical copy, with SHA-256 `190430d6355326281c501057df5a2167782209768ad88ddd62fd66bad29e224c`. The viewer is visible after the navigation beginning at 03:02.013; the action wrapper completed at 03:07.168. The source frames visibly contain JSON before that wrapper completion. This is a verified local representation expressly allowed by the request.

## Scientific claims checked against the recorded export

No article, event page, license or dataset was freshly re-fetched during this video-only revision. Scientific claims were checked against the pinned local real dataset, previously verified provenance and saved independent 80-digit decimal reference in `artifacts/scientific_acceptance.json`. This is a numerical cross-check of the actual new export, not a newly executed experimental validation.

- Dataset: [Jang et al. / Zenodo 18947543](https://zenodo.org/records/18947543), DOI `10.5281/zenodo.18947543`, 483 records, CC BY 4.0; source access date recorded as 2026-10-20. Dataset SHA-256: `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34`.
- Dataset publication: [Charting the Landscape of Oxygen Ion Conductors](https://www.nature.com/articles/s41597-026-07100-x).
- Original comparable source: [Huang et al., J. Am. Ceram. Soc. (1998)](https://doi.org/10.1111/j.1151-2916.1998.tb02662.x), rows 1–3, bulk, two-probe AC, reported 600–1100 K. These are curated source parameters; original full methods/sample conditions remain unverified.
- Formula: sigma = A/T × exp(−Ea/(kB×T)); activation energy meV → eV, prefactor K S/cm, temperature K, conductivity S/cm. All six endpoint values in the downloaded report match the saved independent decimal reference within relative tolerance 1e-12.
- Fixed-regime model roots: 776.4074250510221 K, 817.9098253678244 K and 854.261466339589 K; they match the saved analytic/decimal reference within 1e-9 K. They are calculated intersections, not observed transition measurements. Published fit boundaries are separate; exact T-star results are withheld and ±5 K is an engineering review heuristic, not uncertainty.
- Ranking is conditional within the comparable source group. Atmosphere, preparation, density, sample uncertainty and humidity/lifetime validation are missing. No new material, experiment or uncertainty interval is claimed.
- Recorded genuine DeepSeek executions are historical: B response `8555b7b9-84f2-4553-b7ec-0041482bc9aa`; C response `36ab33a0-d258-4190-a5d4-4d867fd4fe0f`. The source archives and three-request budget ledger are unchanged. Current analysis and export are `OFFLINE_DETERMINISTIC`; replay is explicitly labeled historical and makes zero new inference requests.

## Verification and actual playback

Technical/evidence verification completed at 2026-10-21T07:11:31.219202+00:00. **PASS** applies to the checks below, not to unmet cursor or continuous-browser-playback requirements.

- Both files: 195 seconds, H.264, 1920x1080, 30 fps, 5850 frames, no audio, complete decode.
- 25 ordered minimal-English subtitle cues: at most two lines, 50 characters per line, under 20 characters/second.
- 9 protected old media, PDF, submission copy, replay archives and budget-ledger hashes unchanged.
- Actual downloaded JSON and preview byte-identical; rows, units, orders, six conductivity values and three analytical roots match the saved independent decimal reference.
- Eight accepted source takes: scheduled actions completed within cuts, manifest hashes valid, playback speed 1x.

35 actual decoded final frames and a contact sheet were inspected, including the selection and Analyze states, 700/1000 K orders, intermediate slider positions, all three crossings, B tool/arguments, C abstention, source rows/DOI, export, downloaded JSON and final GitHub URL. No blue text-selection artifact, unwanted blank padding, sidebar template or synthetic cursor was accepted. The primary results are readable at full-size 1920×1080.

**IAB playback: PARTIAL.** Actual IAB playback started and advanced, but continuous attempts stalled at 4.3262 seconds, 8.681073 seconds, and 161.089563 seconds after seeking to 156. The media element reported readyState 2 and error null. Seeking to 42, 156 and 193 seconds displayed decoded frames with readyState 4; a real browser-player guard screenshot was saved. Full continuous playback to 195 seconds was not verified. Both final MP4s separately passed complete FFmpeg decoding; this does not substitute for continuous-browser-playback evidence. Windows QA also encountered WinError 1455; the exact cause of browser stalls remains unconfirmed.

The initial QA extractor failed once in FFmpeg and then with Windows `WinError 1455` (page file too small). It was changed to a single decoder process with bounded threads; the final verification command completed with exit code 0. The first render correctly rejected transient mismatched dimensions in F; the corrected accepted F-ready take passed. These failed attempts were not counted as passes.

| File | Bytes | SHA-256 |
|---|---:|---|
| oxyproof-browser-demo-clean.mp4 | 5656725 | `bc4f6f41cafb8da90c42ebf271f196a1894c4f429ad3264560de7b0c936bd7c2` |
| oxyproof-browser-demo-subtitled.mp4 | 5905298 | `c005ccba5bfdccb6a6ac90bfc628bd79d04203cd240cdbae1e7cedf244e321d1` |

## Changed files and run commands

Only the new `output/osi-final/browser-demo/` namespace and private `.local/browser-demo-capture/` / `.local/browser-demo-render/` working assets were created. Product source code, scientific algorithms, dependency locks, historical acceptance records, PDF, submission copy and old explainer videos were not changed. Git HEAD remains `4286620b13f57c5a5f30af9e00302b0c19259b07`; no commit, push, deployment, upload or submission occurred.

Primary files: `oxyproof-browser-demo-clean.mp4`, `oxyproof-browser-demo-subtitled.mp4`, `oxyproof-browser-demo.srt`, `BROWSER_DEMO_NARRATION.md`, `BROWSER_DEMO_ACCEPTANCE.md`. Supporting review files include the production/validation/report scripts, PLAYER.html, JSON export/proofs, protected hashes, acquisition provenance, verification.json, browser-playback.json and screenshots.

Run from `D:\workshop\oct\oxyproof-osi-2026`:

```powershell
# Verification: actually executed, exit 0
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/validate_browser_demo.py
# Rebuild acceptance from saved evidence
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/write_acceptance.py
# Local review server; the existing instance already listens on 127.0.0.1:8017
.\.local\pdf-venv\Scripts\python.exe output/osi-final/review/scripts/serve_review.py --port 8017
# Production render: already executed; refuses to overwrite existing MP4s
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/produce_browser_demo.py
```

Review URL: http://127.0.0.1:8017/browser-demo/review/PLAYER.html. The real repository URL in the closing overlay is https://github.com/miku-wwl/oxyproof-osi-2026 (also matches local origin).

Backend/frontend regression tests were **NOT RUN** in this media-only revision; no product changes were made. Historical test counts are not presented as current results. The actual new verification is the media/evidence command above.

## Remaining limits and next actions

1. Full acceptance still requires a recording capability that captures the real system pointer while respecting the owner’s IAB-only boundary. The present documented API exposes no such capability. Do not add an artificial pointer to claim completion.
2. Native browser chrome/address bar is absent; the delivered footage captures the genuine webpage viewport. Browser continuous-playback evidence is limited exactly as stated above.
3. Record owner narration if desired; the requested clean and subtitled masters remain silent.
4. Human review/submission remains outside this revision. No public action is authorized or performed.
