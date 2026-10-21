# Final video acceptance - 21 October 2026 NZDT

BROWSER_RECORDING_STATUS=PASS  
VIDEO_RENDER_STATUS=PASS  
VIDEO_DURATION_SECONDS=215.0  
CLEAN_MP4_STATUS=PASS  
SUBTITLED_MP4_STATUS=PASS  
SRT_STATUS=PASS  
NARRATION_STATUS=READY  
ONE_PAGE_PDF_STATUS=PASS  
DEEPSEEK_REPLAY_ACCURACY=PASS  
SCIENTIFIC_CLAIMS_STATUS=PASS

## Actual installed skill and execution

The owner's **IAB Browser Video** skill is the installed **codex-iab-video-recording** package. Its `agents/openai.yaml` declares `display_name: "IAB Browser Video"`, while `SKILL.md` declares the internal name `codex-iab-video-recording`. These are two identifiers for the same skill, not different recording workflows. The installed path is:

`C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md`

It was read in full with `references/REPRODUCTION.md`, `scripts/capture_iab.mjs` and `scripts/render_iab.py`. Its actual sampler was dynamically imported inside `mcp__cua_repl`, controlling **ChatGPT in-app browser, type iab, browser 2, application tab 1**. The local filesystem, local app, binary capture writes and renderer were all accessible. No substitute external browser or native desktop recorder was used. Post-review identity correction: the initial report overlooked `agents/openai.yaml` and incorrectly framed the display/internal-name difference as a missing name match. The YAML's SHA-256 matches the skill's existing manifest; the installed configuration was not changed.

An 8.051-second preflight acquired 61 genuine frames, average 7.577 fps; the skill renderer produced an 8.067-second H.264 MP4, fully decoded it and extracted inspected frames. Formal takes then recorded actual scrolling, slider key presses, rankings, archive loading, scenario B/C replay, expanded arguments/results, source records and real JSON download. Final editing is implemented in `scripts/produce_media.py` using the verified timestamp/hash manifests.

## Measured properties

| Property | Clean | Subtitled |
| --- | --- | --- |
| Duration | 215.000 s | 215.000 s |
| Dimensions / aspect | 1920 x 1080 / 16:9 | 1920 x 1080 / 16:9 |
| Codec / format / range | H.264 / yuv420p / tv | H.264 / yuv420p / tv |
| Export cadence / frames | 30 fps / 6450 | 30 fps / 6450 |
| Audio streams | 0 | 0 |
| Full FFmpeg decode | PASS | PASS |
| Bytes | 4,963,670 | 5,657,769 |
| SHA-256 | `d6e39ff1588b7e339a6f88f98fe71d27c7293bbc6e327abd148780871b949616` | `62be7bf54248f1955f9257bed5751a3a8a5ba874e5da7bbdbb04777b04fd5301` |

These are silent review masters. A narrated version does not exist. The clean version has editorial scientific titles and replay labels, with no burned narration captions; the subtitled version adds the English SRT text in a reserved lower strip.

Accepted source screenshots are **1441 x 811** pixels, captured at **9.137-10.936 fps average**, maximum gap **0.980 s** across accepted takes. Exporting 1080p/30 does not claim native 1080p/30 capture or create additional motion detail. Full viewport is aspect-fitted at 1536 x 864, with header/side annotations outside the app image. No scientific UI was reconstructed, no cursor animation was invented and no app code was changed. All accepted takes play at 1x and are trimmed to whole-second lengths; a separate 15-second editorial closing card completes the video.

The first C/source takes changed dimensions during recording and became too small after fitting. Those raw takes are preserved privately and excluded from the final edit. Readable replacements are `scene4-final` and `scene5-final`; the former inspects the already-replayed C result. The earlier 204.76-second WebM was inspected, but its baked captions and 1440 x 1000 framing were incompatible with the clean master. It was preserved without modification.

## Scene-by-scene visual acceptance

| Final time | Accepted result | Decoded samples |
| --- | --- | --- |
| 00:00-00:25 | Real research dashboard; published scope and operating-condition question | 1, 12, 24 s |
| 00:25-01:25 | Real conductivity curves; slider; 700 K 1>2>3 and 1000 K 3>2>1; 776/818/854 K model event cards; separate T* qualifications | 31, 37, 50, 62, 72, 84 s |
| 01:25-02:10 | Load saved real execution evidence, replay B, provider/model/tool, typed arguments, deterministic result and independent audit | 87, 102, 113, 125 s |
| 02:10-02:50 | C question includes humidity/lifetime; screen proposal, independent refusal origin, zero candidates, no executed calculation and proposed future measurement | 135, 147, 160, 169 s |
| 02:50-03:20 | Actual curated formulas, DOI, LT/HT parameters/units, source metadata and successful real report download | 172, 185, 197 s |
| 03:20-03:35 | Complete project, event and GitHub closing card | 201, 207, 214 s |

All 23 subtitled decoded samples and four contact sheets were visually inspected; key clean frames at 37 and 214 s and detailed C/source views were inspected at full resolution. Text/claims are consistent, captions stay outside the app, the closing is complete, and no credential, notification, unrelated tab, loading/error screen or fabricated science is visible in the inspected final samples. The underlying app uses small technical metadata text; view the full 1080p file for those details. Selected-frame review does not imply human inspection of every frame.

The finished subtitled MP4 was also played in the IAB review page. Actual browser duration 215 s, intrinsic dimensions 1920 x 1080, readyState 4 and no media error were observed; final playback observations are in `browser-playback.json`. The first ordinary HTTP preview stalled at 135.944 s and seeking reset playback. A separate loopback byte-range server replaced it: actual HTTP 206/32-byte retrieval, seeking to 130 s, continued playback beyond 164 s and natural arrival at **215 s / ended=true / error=null** were verified. This fixes the review transport without editing the video; the initial failed playback is disclosed. FFmpeg fully decodes both complete files. No narration listening or audio mix is claimed.

## Caption and PDF checks

The SRT has **40 sequential cues**, no overlap, maximum two lines / 49 characters per line, maximum **19.55 characters/s**, final cue end **214.6 s**. Its exact spoken text is the **456-word** script: **127.3 words/minute** across the edit including pauses. Timings align with actual slider states, replay evidence and report export. Voice recording is pending, so final spoken delivery cannot yet be checked.

The revised PDF is exactly **one A4 page** (595.276 x 841.890 pt), rendered with Poppler/MiKTeX at 150 dpi and visually inspected after correcting a legend/700 K annotation overlap. Final figure, formulas, limitations, sources and footer are legible without clipping or overlap. PDF text/page checks pass. MiKTeX printed `Syntax Error: No display font for 'Symbol'`; rendering still exited 0 and the inspected final page has no missing glyphs. ReportLab invariant metadata uses its fixed epoch for reproducibility; source verification and review dates are explicitly printed in the document.

Exact probe/decode, SRT, archive/export and protected-original results are in `media-validation.json`, `ffprobe-clean.json`, `ffprobe-subtitled.json` and `capture-and-edit-provenance.json`.
