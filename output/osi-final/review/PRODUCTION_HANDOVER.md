# OxyProof final production handover - 21 October 2026 NZDT

The finished local review package contains a genuine-app 03:35 silent demonstration in clean and English-subtitled variants, a synchronized owner-recording script/SRT, a redesigned one-page scientific PDF, submission/social drafts and reproducible media QA. **No new inference, publication or submission occurred.** Application and scientific source files were not edited.

## Delivery paths

All paths below are relative to `D:/workshop/oct/oxyproof-osi-2026/output/osi-final/`:

- `video/oxyproof-final-clean.mp4`
- `video/oxyproof-final-subtitled.mp4`
- `video/oxyproof-final.srt`
- `narration/NARRATION_FINAL.md`
- `submission/oxyproof-one-page-final.pdf`
- `submission/SUBMISSION_FINAL.md`
- `submission/SOCIAL_POST_FINAL.md`
- `review/VIDEO_ACCEPTANCE.md`
- `review/SCIENTIFIC_CLAIMS_REVIEW.md`
- `review/SUBMISSION_CHECKLIST.md`
- `review/PRODUCTION_HANDOVER.md`
- `review/REVIEW.html` - local finished-media player
- `review/screenshots/` - final decoded QA frames, contact sheets and rendered PDF
- `review/flagship-conductivity.png`, `.svg`, `flagship-plot-input.csv`, `figure-provenance.json`
- `review/exported-decision.json` - actual application download, not a reconstructed report
- `review/media-validation.json`, `ffprobe-clean.json`, `ffprobe-subtitled.json`
- `review/capture-and-edit-provenance.json`, `browser-playback.json`
- `review/scripts/` - figure, PDF, media, verification and ZIP production scripts
- `SHA256SUMS.txt` - exact payload paths/hashes
- `oxyproof-final-review-package.zip` and `.zip.sha256`
- `review/package-verification.json` - post-build verification outside the ZIP to avoid self-reference

The ZIP contains the actual completed deliverables and QA files. Raw frames, virtual environments, tools/binaries, full data copies and browser state are excluded. `SHA256SUMS.txt` is the exhaustive created-payload inventory. ZIP CRC, duplicate/path safety and every entry hash are checked by `scripts/package_review.py`.

## Actual skill workflow and private sources

Installed skill: `C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md`. This is the owner's **IAB Browser Video** skill: `agents/openai.yaml` sets that UI display name, and `SKILL.md` sets the internal ID `codex-iab-video-recording`. The initial report overlooked the display-name configuration; that identity statement is corrected here. The skill's actual `capture_iab.mjs` was imported in the browser-capable REPL, and its `render_iab.py` completed the preflight. Browser 2/type iab controlled actual local application tab 1. No desktop, external Chromium/Playwright browser, synthetic screenshots or native recorder substituted for new footage. No skill configuration or video was changed by this correction.

Private source: `D:/workshop/oct/oxyproof-osi-2026/.local/osi-final-capture/`. Accepted take names: `scene1`, `scene2a`, `scene2b`, `scene3a`, `scene3b`, `scene4-final`, `scene5-final`. Every frame has its original hash and monotonic capture time in its capture manifest. Preflight and discarded variable-size takes remain there; intermediate edits are preserved in `.local/osi-final-render/first-edit/`. They are not included in the review ZIP.

Seven genuine app takes supply 200 seconds at 1x; an explicitly editorial closing card supplies 15 seconds. No app code was modified for filming. Accepted images are 1441 x 811, average 9.137-10.936 fps, with max intersample gap 0.980 s; final export is 1920 x 1080/30 fps. Upscaling is disclosed. Source hashes, events, crops (none), whole-second trims and presentation overlays are recorded in the provenance JSON.

Existing `.local/demo-phase25/oxyproof-phase2.webm` and `output/pdf/oxyproof-one-page-submission.pdf` retain their original SHA-256 hashes. The old clip was genuinely inspected, but baked captions prevented use as a clean narration master. New browser filming replaced it without overwriting it.

## Review / run commands

Run from `D:/workshop/oct/oxyproof-osi-2026`:

```powershell
.local/pdf-venv/Scripts/python.exe output/osi-final/review/scripts/serve_review.py --port 8017
```

Open `http://127.0.0.1:8017/review/REVIEW.html`. A loopback review server was started for current verification; if the port is already serving this page, reuse it. It is a review player, not a public deployment. The scientific app remains at `http://127.0.0.1:8000`. Use this range-capable server for browser seeking; the initial ordinary `http.server` preview stalled, and was replaced without changing the MP4s. A real 206 byte-range response and forward playback past the former stall were verified.

Existing app startup with cached dependencies/data/build:

```powershell
$env:OXYPROOF_DISABLE_CLOUD = '1'
uv run --offline --no-sync python scripts/start.py --offline
```

Production commands actually used (existing PDF environment; global Python supplies matplotlib):

```powershell
python output/osi-final/review/scripts/make_figure.py
node 'C:/Users/weila/.codex/plugins/cache/openai-primary-runtime/pdf/26.1015.12040/skills/pdf/container_tools/mark_artifact_operation_started.mjs' --operation-kind create --expected-output-count 1 --output-format pdf
.local/pdf-venv/Scripts/python.exe output/osi-final/review/scripts/make_pdf.py
pdftoppm -png -r 150 -singlefile output/osi-final/submission/oxyproof-one-page-final.pdf output/osi-final/review/screenshots/one-page-final
.local/pdf-venv/Scripts/python.exe output/osi-final/review/scripts/produce_media.py
.local/pdf-venv/Scripts/python.exe output/osi-final/review/scripts/validate_media.py
uv run --offline --no-sync python -m pytest tests/test_recorded_deepseek.py -q
.local/pdf-venv/Scripts/python.exe output/osi-final/review/scripts/package_review.py
```

The PDF marker was run successfully exactly once before first authoring; it is not needed for read-only review. PDF/media scripts need Pillow, ReportLab and pypdf in the existing `.local/pdf-venv`; figure script uses existing matplotlib. No formal project dependency changed. Renderer refuses an existing MP4: preserve or choose another output before a deliberate re-edit, rather than replacing originals. The figure/PDF and QA scripts target only this production output tree. The media script needs retained private capture manifests; the review ZIP alone is not a complete raw-capture archive.

Actual media tools: `.local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin/ffmpeg.exe` and `ffprobe.exe`. Download source directly verified 21 October: https://www.gyan.dev/ffmpeg/builds/ . Release ZIP SHA-256 `60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba` matched the publisher checksum. Tools stay private/ignored and are not redistributed. The existing imageio FFmpeg 7.1 executable was used only for initial old-footage inspection.

## Actual validation and limits

- Both final MP4s: 215.000 seconds, 1920 x 1080, H.264/yuv420p/tv, 30 fps, 6450 frames, zero audio streams. Complete decode PASS; final decoded samples/contacts visually reviewed. Browser playback was exercised; final observations are in `browser-playback.json`.
- SRT: 40 cues, max two lines / 49 characters, max 19.55 characters/s, no overlap, last cue 214.6 s. Narration: 456 words, 127.3 words/minute across the video. No voice or music generated or mixed.
- PDF: exactly one A4 page, final render inspected. A nonfatal MiKTeX Symbol-display-font warning is retained in `VIDEO_ACCEPTANCE.md`; no missing glyph or clipping appears on the reviewed page.
- **This sprint actually ran:** `9 passed, 1 warning in 0.55s` for archived DeepSeek replay tests. The warning is the existing Starlette/httpx deprecation. Asset checks verify complete decodes, subtitles, source/export ordering, three archived requests and unchanged original hashes.
- **Historical, not rerun here:** 255 backend, 12 component, 21 Chromium tests; 49/49 hand-selected integrity cases, 5/5 offline cases and 3/3 genuine DeepSeek scenarios. Supporting files remain in the repository. No generalized accuracy claim follows.

The model/provider and local scientific results are real. Replay uses `RECORDED_TRACE_REPLAY` and `fresh_model_request=false`; it is not new inference. C's model-selected screen was blocked by independent constraint auditing, with no executed scientific calculation or candidates. The budget remains at exactly three historical attempts; no key or provider setting was changed. Original capture and current normalized application telemetry remain preserved as documented in `docs/DEEPSEEK_LIVE_ACCEPTANCE.md`.

The science plot is derived from archived engine samples; no scientific values or article illustrations were invented. Dataset DOI `10.5281/zenodo.18947543`, CC BY 4.0; original study DOI `10.1111/j.1151-2916.1998.tb02662.x`. Source verification was 20 October, current production checks were 21 October. No original full methods/Table 3, row-specific sample conditions, validated uncertainties, humidity tolerance or lifetime evidence has become available. Rankings remain conditional and model roots require experimental confirmation.

## Public state and owner actions

Public repository: https://github.com/miku-wwl/oxyproof-osi-2026 . Read-only remote main and local production entry matched `4286620b13f57c5a5f30af9e00302b0c19259b07`. Only new production files under `output/osi-final/` were added; no tracked application/science/evidence files were changed, staged or committed. Raw media/tool files are ignored under `.local/`.

Registration and eligibility of October 20 development are confirmed by the owner and are no longer unresolved gates. The current 2026 agenda was checked directly: https://llmhackathon.github.io/agenda/ . It describes a social post with up-to-four-minute optional video/presentation and up-to-one-page description, deadline **23 October 2026 13:00 NZDT**. The separately inspected `/submission/` page still says September 12/two minutes/Google Form; it conflicts and is not used as current authority. Attendee confirmation is still required for the final channel/form and any newer Slack instructions.

Owner's remaining actions: review assets, record voice if desired, approve any later mix/upload, confirm current routing, replace marked public-video/PDF URL placeholders after an authorized upload, then approve publication/formal entry. The current video/PDF are production-complete for local review, not proof of submission. No commit, push, deployment, upload, social post or entry submission occurred.
