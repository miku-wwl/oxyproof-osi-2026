# Final demo acceptance - 2026-10-20 NZDT

**VIDEO_ACCEPTANCE_STATUS=PASS; ONE_PAGE_SUBMISSION_STATUS=READY for owner review.** No upload or submission occurred.

The original `.local/demo/oxyproof-phase2.webm` exists and was actually inspected: 204.4s, 1440x1000, 25 fps, VP9/WebM, no audio. Its SHA-256 remains `3169945007ec4bdf773e7907f2708774a8bc76945c3ad7bd5589f3225dd6b3a3`. Original media, scene log and export are preserved. It is superseded for presentation by a separately captured version with public rounding and explicit uncertainty language.

Accepted updated recording: **`.local/demo-phase25/oxyproof-phase2.webm`**, **204.76 seconds**, **1440x1000**, **25 fps**, **no audio stream**. `artifacts/final_demo_validation.json` records hash, size, metadata and capture code version. `.local/demo-phase25/exported-decision.json` is an actual browser download. The record test used the real Python API, not mocked responses.

Review method: media inspection with Playwright's FFmpeg binary; frames extracted four seconds into every captioned scene and two seconds before the end. All ten scene frames plus the near-end frame were visually inspected in this sprint, for both the original and updated assets. This is representative-frame acceptance, not a frame-by-frame or human-listening claim. No audio exists.

| Scene | Observed acceptance evidence |
| --- | --- |
| 1 | Scientific question and value visible; OFFLINE_DETERMINISTIC and 483-record labels |
| 2 | Real log-scale curves, original formulas, T* dashed lines, engineering-neighborhood label |
| 3 | 700 K ordering 1 > 2 > 3, numeric backend values |
| 4 | 1000 K ordering 3 > 2 > 1 |
| 5 | Rounded roots approximately 776, 818, 854 K, distinct T* events; caption explicitly states uncertainty unavailable and experimental confirmation required, held 22 seconds |
| 6 | Exact T* row withheld, no continuity assumption, +/-5 K explicitly heuristic |
| 7 | Wrong formula rejected with K S/cm units; source DOI and model shown |
| 8 | Humidity constraint retained in refusal, no candidate recommendation, proposed measurement |
| 9 | Three formulas, both fit regimes, provenance/raw parameters, exported code fingerprint |
| 10 / tail | Contribution and limits held legibly through the end |

Captions and key results are readable at native resolution. Inspected frames contain no visible secrets/private account UI, browser error page, empty result panels or misleading fabricated transitions. The overlay is presentation text over genuine UI, not app-generated evidence. Raw scientific tables are technical detail; viewing at a smaller resolution may require pausing/fullscreen. No accessibility certification or external video-player compatibility is claimed. A silent WebM is the delivered format; no MP4 conversion was performed.

The PDF `output/pdf/oxyproof-one-page-submission.pdf` is **one A4 page**, confirmed by pypdf and pdfinfo and visually inspected as a 1500px Poppler PNG. It is legible with no clipping/overlap/missing glyphs. Markdown source: `FINAL_SUBMISSION_COPY.md`; build helper: `scripts/build_submission_pdf.py`; acceptance metadata: `artifacts/pdf_acceptance.json`. Both explicitly disclose absent live LLM acceptance and original-method/uncertainty limitations.

The [2026 agenda](https://llmhackathon.github.io/agenda/) was directly rechecked October 20: October 21-22 event; deadline **October 23 00:00 UTC = October 23 13:00 NZDT**; a social post can include up to four minutes of video/presentation and up to one page of write-up. The [legacy submission page](https://llmhackathon.github.io/submission/) still says September 12 / two minutes and links a form. It is conflicting historical guidance, not silently adopted as the 2026 process. Authenticated attendee Slack was **not checked**; no Slack connector/session was available for this task. Latest Slack instructions prevail, so owner verification remains required.

Neither software/video/PDF acceptance nor a reachable GitHub repository proves registration, pre-event eligibility, media upload, final-form completion or successful submission. See `RELEASE_GATE.md`.
