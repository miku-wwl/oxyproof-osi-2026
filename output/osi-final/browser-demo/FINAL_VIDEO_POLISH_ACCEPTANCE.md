**OxyProof — final video polish acceptance**

```text
VIDEO_POLISH_STATUS=PASS
ENGINEERING_LABEL_REMOVAL=PASS
WINDOWS_CURSOR_STATUS=PASS
CLICK_ALIGNMENT_STATUS=PASS
SLIDER_VISUALIZATION_STATUS=PASS
SCIENTIFIC_CLAIMS_STATUS=PASS
SUBTITLE_STATUS=PASS
VIDEO_DECODE_STATUS=PASS
ORIGINAL_VIDEO_PRESERVED=YES
READY_FOR_OWNER_NARRATION=YES
```

Accepted scope: final media polish only. Ready for the owner to record English narration. These statuses concern preservation and post-production, not a new scientific experiment, new inference or fresh event-rule verification.

New deliverables are `oxyproof-browser-demo-final-clean.mp4` and `oxyproof-browser-demo-final-subtitled.mp4` in `D:/workshop/oct/oxyproof-osi-2026/output/osi-final/browser-demo/`. Both preserve 195.000 seconds (03:15), 1920×1080, 30 fps, 5,850 frames, H.264/yuv420p/TV range, faststart and zero audio streams. Source acquisition remains the previously documented variable IAB screenshot rate; export at 30 fps does not establish native 1080p/30 capture.

| File | Bytes | SHA-256 |
|---|---:|---|
| oxyproof-browser-demo-final-clean.mp4 | 12539257 | `9c43d639724a690da405bbd7e7d4f4575000db0b17f676495614d72c7f517e73` |
| oxyproof-browser-demo-final-subtitled.mp4 | 13231080 | `745218cf82db2ffe6913cc008e8cb8b73993a41daaa605ae7d18ab8d3818e9a3` |

**Exact changes.** Re-composited the accepted original browser MP4s with the existing verified cursor layers. Disabled every added engineering text tag: `Logged target`, `Control highlight`, `Logged drag endpoints · no measured pointer path`, and the brief opening reconstruction/native-capture notice. Disclosure remains here and in the original cursor acceptance/evidence. No compressed-image erasure, inpainting, replacement UI, cropping, zoom, retiming or application re-recording was used. Genuine application text and scientific disclosures remain unchanged.

Kept the same small white arrow, dark outline, 0.4-second click ring, actual control outlines and separate logged slider endpoint cues. All 12 original annotation records, coordinate transforms, logged call windows, dynamic control rectangles and the three actual drag start/end pairs are unchanged. No intermediate pointer positions, connecting trajectories or new clicks were added. Missing/stale coordinates still use a control outline, without a fabricated pointer. Removing the old drag label also reveals arrow-tail pixels it previously covered.

**Pointer provenance.** Indicators are annotated reconstructions from actual IAB interaction logs, not native Windows/system cursor capture. Times identify recorded IAB method request/completion windows, not measured OS mouse-down/up instants. The white Windows-style vector is retained only at previously validated targets/endpoints. All retained effect pixels outside the removed tag footprint were compared against the accepted overlay PNGs on all 363 active frames. Within the removed tag footprint, the original arrow underneath is revealed.

The overlay is active for 12.1 seconds in total; the maximum nonzero-alpha footprint is 1.054% of the canvas. All annotation alpha remains zero at y=996–1079. There is no permanent commentary panel or new title card.

**Sources used, unchanged.** `oxyproof-browser-demo-{clean,subtitled}.mp4`; accepted cursor MP4s; `oxyproof-browser-demo.srt`; `BROWSER_DEMO_ACCEPTANCE.md`; `CURSOR_VISUALIZATION_ACCEPTANCE.md`; `review/recording-provenance.json`; `review/slider-operation-proof.json`; `review/cursor/annotation-plan.json` and existing overlay PNGs; the eight original `.local/browser-demo-capture/{A1,A2,B,B-roots,C,D,E,F-ready}/capture-manifest.json` files. All eight manifest checksums match the original production provenance. The installed IAB skill instructions were read for the rendering/QA boundaries only; no skill renderer was used or modified by this polish task.

**Mandatory QA results.**

| Check | Actual result |
|---|---|
| Engineering labels removed | PASS: the new overlay drawing has no text tags or introductory note; decoded frames inspected |
| Scientific limitations retained | PASS: model-derived crossings, no uncertainty bounds, recorded DeepSeek replay, independent audit, unsupported constraints/abstention remain visible |
| Cursor, click and drag alignment | PASS at original logged-call precision; unchanged geometry/timing; no duplicate cursor seen in reviewed final frames |
| Genuine Replay B/C and export | PASS: recorded trace labels, B tool selection, C refusal and downloaded JSON remain visible |
| Subtitles | PASS: all 25 original cues/timings retained; SRT hash unchanged; no cursor overlay in subtitle strip |
| Both complete MP4 decodes | PASS: full FFmpeg -xerror decodes exit 0; no near-black frames detected |
| Frame timing / segment boundaries | PASS: all 5,850 packet timestamps equal n/30 seconds within 0.00001 s; no timestamp gaps/duplicates |
| Final properties | PASS: 195.000 s each, under 4 min, 1920×1080/30 fps, silent, faststart |
| Original media/source preservation | PASS: 441 protected project/media/document/manifest hashes unchanged |

Visual inspection covered both 34-frame final contact sheets (68 samples) and nine full-resolution final decoded frames. The inspected sequence covers source/material selection, Analyze, all three drag operations and their resulting states, model events/disclosures, Replay B, Replay C, source evidence, Export JSON, the JSON viewer and closing dashboard. No blank scene or unexpected overlay was observed in those samples. Full decoding and black-frame detection cover both complete files; visual inspection is representative, not a claim that every frame was manually viewed.

**Screenshots from final MP4s.**

- [Analyze before/after](review/polish/analyze-before-after.jpg) and [slider before/after](review/polish/slider-before-after.jpg). These comparison labels are QA images only, not in the videos.
- [Analyze at 28.33 s](review/polish/clean-qa-08.jpg), [second drag at 53.25 s](review/polish/clean-qa-14.jpg), [1000 K endpoint at 58.25 s](review/polish/subtitled-qa-17.jpg).
- [Replay B after reflow at 108.8 s](review/polish/clean-qa-24.jpg), [Replay C after reflow at 136.8 s](review/polish/clean-qa-28.jpg).
- [Scientific crossing disclosure at 91 s](review/polish/subtitled-qa-22.jpg), [genuine recorded B trace at 113.5 s](review/polish/subtitled-qa-25.jpg).
- [Export at 177.45 s](review/polish/subtitled-qa-31.jpg), [downloaded JSON at 184 s](review/polish/subtitled-qa-33.jpg).
- [Clean contact sheet](review/polish/clean-contact.jpg) and [subtitled contact sheet](review/polish/subtitled-contact.jpg).

**Scientific preservation.** The original footage still shows conditional row order 1 > 2 > 3 at 700 K and 3 > 2 > 1 at 1000 K; approximately 776/818/854 K model-derived crossings; separate published fit boundaries; no experimental uncertainty bounds; historical DeepSeek replay with zero new inference; independent evidence auditing; humidity/lifetime abstention; original source DOI and the actual JSON export. No scientific values, traces, model results, rankings or claims were recalculated or edited. Source references and qualifications remain in the original browser acceptance report and exported decision.

**Run commands actually executed from the repository root.** Each final stage completed with exit 0. These commands intentionally refuse to overwrite existing deliverables/evidence; the files now exist.

```powershell
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/render_final_polish.py prepare
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/render_final_polish.py render
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/render_final_polish.py verify
```

Actual outputs: `PREPARED 363 effect frames; 363 retained effect comparisons; protected 441`; both `RENDERED` lines; both `FULL_DECODE_PASS` lines; `VERIFICATION_PASS; visual inspection pending; 441 protected files unchanged`. Visual inspection subsequently passed and is recorded separately in `review/polish/visual-review.json`; `verification.json` now references that result.

Encoding uses bounded one-frame RGB compositing, seven exact-frame segments per edition, single-thread decoding/encoding, a one-packet raw input queue and x264 veryfast/zerolatency CRF 14. Segments are joined by stream copy, with an explicit limited-range H.264 flag and faststart. No additional image encode occurs during concat. This is ordinary lossy re-encoding, not a byte-identical image copy; decoded scientific text readability was checked.

**Failures and scope notes.** The first full-length clean encode failed with `BrokenPipeError` after FFmpeg reported `Error during demuxing: Cannot allocate memory`. Windows reported less than 1 GB available virtual commit. Its partial intermediate and logs are preserved privately in `.local/final-video-polish/`; it is not a deliverable. The final bounded-segment renders and complete QA passed. Initial layer comparison also exposed the old text tag overlapping an arrow tail; the corrected check distinguishes removed tag paint from retained vector geometry.

The initial 450-file monitoring snapshot includes eight installed-skill files and one Python cache. A separate skill-upgrade workflow concurrently changed several installed-skill files; this task did not write to that installation or restore those outside changes. The first import refreshed one derived project Python bytecode cache; further bytecode writes were disabled. Those nine out-of-scope/cache entries are excluded from the immutable 441-file project/media/document set. Exact observed differences are in `review/polish/out-of-scope-drift.json`; the original snapshot is `.local/final-video-polish/protected-before.json`. Accepted videos, SRT, narration, source scripts, app/scientific code, source manifests and prior reports all match their initial protected hashes.

**Remaining limitations.** Continuous browser/player playback was NOT RUN in this polish revision. Complete FFmpeg decoding, timestamp checks and representative final-frame review passed; the older IAB buffering limitation is not claimed resolved. Native OS cursor capture remains unclaimed. Owner listening/narration approval is pending because both masters intentionally contain no audio. Backend/frontend tests were NOT RUN for this media-only change.

Changed scope: the two new final MP4s, this report, `review/render_final_polish.py`, supporting evidence/QA under `review/polish/`, and private `.local/final-video-polish/` caches/logs. No browser re-recording, app-code edit, model request, AI narration, dependency/OS change, commit, push, upload, deployment, publication or submission was performed. Git HEAD remains `816fc06328561f82f0656bf20cd8a60ef31cc3c0`. The next action is owner review and separate English narration.
