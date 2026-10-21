"""Generate the cursor-annotation handover from verified local artifacts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
REVIEW=OUT/'review/cursor'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def stamp(t):
    m,s=divmod(t,60);return f'{int(m):02}:{s:06.3f}'
def main():
    p=read(REVIEW/'annotation-plan.json');v=read(REVIEW/'verification.json');visual=read(REVIEW/'visual-review.json')
    assert v['technical_status']=='PASS' and v['visual_review']=='PASS' and visual['status']=='PASS'
    lines=['# OxyProof — cursor visualization acceptance','',
    'SPRINT_STATUS=PASS (the owner-authorized annotation task)',
    'CURSOR_ANNOTATION=PASS',
    'CLICK_SYNCHRONIZATION=PASS_WITH_LOGGED_CALL_WINDOW_PRECISION',
    'SLIDER_ENDPOINT_VISUALIZATION=PASS',
    'VIDEO_DECODE=PASS',
    'VISUAL_REVIEW=PASS',
    'ORIGINAL_ASSETS_UNCHANGED=PASS',
    'NATIVE_MOUSE_CAPTURE=NOT_CLAIMED',
    'NEW_REAL_ACTIONS=0',
    'NEW_MODEL_CALLS=0','',
    '**These pointer indicators are reconstructed annotations from actual IAB interaction logs, not native system mouse capture.** The owner explicitly authorized this reconstruction. White cursor glyphs identify verified logged targets or actual drag-call endpoints. They do not establish an unrecorded mouse position, motion path or exact operating-system mouse-down time. Missing or stale geometry uses a clearly labeled **Control highlight**, with no invented cursor position or click pulse.','',
    '## New deliverables','',
    '- `oxyproof-browser-demo-cursor-clean.mp4`: accepted clean footage plus sparse, disclosed annotations; no narration subtitles or audio.',
    '- `oxyproof-browser-demo-cursor-subtitled.mp4`: accepted subtitled footage plus the identical annotations; original subtitle timing retained; no audio.',
    '- `CURSOR_VISUALIZATION_ACCEPTANCE.md`: this report.','',
    'Both MP4s preserve the complete 195.000-second / 03:15 timeline, all 5,850 frames at 30 fps, 1920×1080, H.264/yuv420p/TV range and faststart. They are below four minutes. Underlying IAB acquisition remains the original 6.564–12.514 fps across takes; annotation/export at 30 fps does not add native capture detail. The owner will record narration separately. No application re-recording or browser interaction occurred in this revision.','',
    '## Evidence read and protected','',
    '- `output/osi-final/browser-demo/review/recording-provenance.json`',
    '- `output/osi-final/browser-demo/review/slider-operation-proof.json`',
    '- `output/osi-final/browser-demo/BROWSER_DEMO_ACCEPTANCE.md`',
    '- Original `.local/browser-demo-capture/{A1,A2,B,B-roots,C,D,E,F-ready}/capture-manifest.json` and hashed source frames.',
    '- The actual installed `C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md` and its capture script. The skill permits explicitly disclosed lightweight marks on genuinely recorded clicks. Its IAB-only recording boundary remains respected; this task is post-production on the already accepted footage.','',
    'The evidence logs contain two different things: DOM element centers measured before a locator click, and explicit native IAB drag-call coordinates. The former can become stale when the locator scrolls the page before clicking. All candidate locations were checked against the preserved frame at the actual action time; a non-null point alone was not treated as proof of a valid cursor location.','',
    '## Coordinate mapping','',
    'The recorded screenshots are 1921×1081, including unused capture padding. Recorded CSS viewport: 1934×1088, reported DPR 1.100000071773927. The original production used source crop `[0,0,1749,984]`, then Pillow `ImageOps.fit` to 1920×1080. The content-rectangle registration was checked on the preserved visible controls. It is not an independent native-pointer calibration; suspect or moving targets fail closed to highlights. Multiplying CSS coordinates by DPR would be incorrect for this recorded, scaled capture footprint.','',
    '```text',
    'raw_x = css_x * 1749 / 1934',
    'raw_y = css_y * 984 / 1088',
    'scale = 1920 / 1749 = 1.097770154373928',
    'fit_vertical_trim = (984 - 1080/scale) / 2 = 0.09375 source px',
    'out_x = raw_x * scale',
    'out_y = (raw_y - 0.09375) * scale',
    '```','',
    'The 0.09375-pixel trim on each vertical edge reproduces the original aspect-preserving ImageOps.fit, rather than independently stretching height. The mapped points are checked inside the actual output-control rectangles. They identify logged target positions, not measured native-pointer pixels. Source footage, crop, scale, scene cuts and displayed data were not changed.','',
    '## Annotated actions and timing','',
    'Timing comes from actual monotonic IAB request/completion records plus the source-take offsets in recording-provenance.json. The rings last approximately 0.4 seconds (12 output frames) and mark the logged call cue; the logs do not expose the exact internal OS click instant. The visible state changes were checked separately. All annotations occur within or immediately after the corresponding genuine call window; no new action is suggested.','',
    '| Action | Actual call window | Annotation window | Method |','|---|---|---|---|']
    for a in p['annotations']:
        x,y=a['call_interval_s'];s,e=a['video_interval_s']
        method={'logged_target':'White target cursor + 0.4 s ring','control_highlight':'Labeled control highlight; no cursor/click pulse','drag_endpoints':'Two logged endpoints; no connecting trajectory'}[a['kind']]
        lines.append(f"| {a['id']} | {stamp(x)}–{stamp(y)} | {stamp(s)}–{stamp(e)} | {method} |")
    lines += ['',
    'Two stationary click-target glyphs are used: source-group selector and Analyze. All three record-selection clicks use control highlights because auto-scroll makes their pre-click geometry stale during the cue. Replay B and Export have null coordinate evidence. Replay C has a pre-scroll bottom-edge point that becomes stale and would overlap the existing subtitle area. These cases use verified control highlights. The source-group selection uses selectOption rather than an invented mouse click.','',
    'The labeled row and replay/export highlights follow vertical page changes by matching actual preserved control-label pixels at each output-frame timestamp. This tracks the CONTROL, never an unrecorded pointer. Verified before/after templates account for selection/hover text-tone changes, so a faded selected row is not mistaken for its unselected neighbor. Registration is limited to vertical translation; the reference images/ROIs, match scores, alternative-location scores and per-frame output rectangles are saved in annotation-plan.json and control-registration.json. The final visual review checks the beginning and end of each cue after UI reflow.','',
    'A candidate highlight for opening the record disclosure was rejected during preview because auto-scroll moved the target onto a list row. It is absent from the final annotation schedule. Selection of the actual three records remains visible and annotated.','',
    '| Logged drag | Original start/end CSS coordinates | Mapped output positions | Actual index change |','|---|---|---|---|']
    for a in p['annotations']:
        if a['kind']=='drag_endpoints':
            points=' → '.join(f'({x:.2f}, {y:.2f})' for x,y in a['output_endpoints'])
            lines.append(f"| {a['id']} | {a['source_from_css']} → {a['source_to_css']} | {points} | {a['before_index']} → {a['after_index']} |")
    lines += ['',
    'The slider footage itself shows the genuine changes from 700 K through approximately 805.545 K and 900 K to 1000 K. Only the recorded start/end pointer positions are shown: a short start glyph, a gap, then an end glyph. Small endpoint circles and the label “Logged drag endpoints · no measured pointer path” explain them. No interpolated pointer, connecting path, intermediate input samples or additional clicks were synthesized.','',
    'All indicators are brief. A small 2.6-second introduction discloses the reconstruction; there is no permanent title/banner or commentary layout. Cursor geometry is a small white arrow with a dark outline, approximately 18×27 pixels. Rings are subtle, and target highlights are outlines rather than opaque UI replacements. Labels appear beside the relevant controls in unused space.','',
    f"The overlay is nonempty on {v['overlay_nonempty_frames']} of 5,850 frames ({v['overlay_nonempty_frames']/30:.1f} seconds, including the disclosure). All overlay alpha is zero in y=996–1079, preserving the existing subtitle strip and its timing. No new SRT was written; the original SRT SHA-256 remains `{v['original_srt_sha256']}`.",'',
    f"The maximum annotation footprint, counting every nonzero-alpha pixel including anti-aliasing, is {v['maximum_annotation_canvas_fraction']*100:.3f}% of the canvas. Even when combined with the existing 84-pixel subtitle strip, more than 90% of the application remains unobstructed.",'',
    '## Quality acceptance','',
    '| Requirement | Result | Evidence |','|---|---|---|',
    '| 1. Positions align with controls | PASS within evidence limits | Eight logged target/endpoint positions checked on actual controls; seven missing/stale/semantic cases use labeled highlights |',
    '| 2. Click synchronization | PASS at logged-call precision | Actual request/completion windows; 0.4-second ring cues, no claim of exact OS event timing |',
    '| 3. Slider changes understandable | PASS | Actual 0 → 31 → 60 → 92 input states, separate endpoint glyphs, visible real temperature changes |',
    '| 4. No fake actions | PASS | Every annotation references an existing recorded action; zero new browser/model calls; no intermediate pointer trace |',
    '| 5. Readability | PASS | Final decoded frames inspected at full resolution; no annotation in original subtitle strip or replacement of scientific text |',
    '| 6. MP4 full decode | PASS | Both completed ffmpeg -v error -xerror full decodes with exit 0 |',
    '| 7. Below four minutes | PASS | Both 195.000 s, 5,850 frames, 30 fps |',
    '| 8. Original videos unchanged | PASS | SHA-256 before/after, plus other protected source/document/archive hashes |','',
    'Checkbox image checks directly confirm each of rows 1, 2 and 3 changes from unchecked to checked in the original source images. The selected-control marker coordinates are not used to invent those states. The full before/after evidence and source frame hashes are saved in `review/cursor/source-state-evidence.json` and `checkbox-state-checks.json`.','',
    f"Technical verification finished at {v['verified_at_utc']}. {visual['summary']}",'',
    'Final-frame contact sheets: [clean](review/cursor/clean-contact.jpg) · [subtitled](review/cursor/subtitled-contact.jpg). The saved independent scientific reference/export, 700 K order 1 > 2 > 3, 1000 K order 3 > 2 > 1, source DOI, 776/818/854 K model crossings, warnings and historical genuine DeepSeek replay labeling remain the accepted original footage. Scientific calculations were not rerun or altered in this annotation task. No new data, experiments, uncertainty estimates or model inference are claimed.','',
    'Continuous IAB player replay was NOT RUN in this post-production revision. Complete FFmpeg decoding and final-frame visual checks were run. The prior browser-player buffering limitation in BROWSER_DEMO_ACCEPTANCE.md is preserved; this report does not silently turn that historical partial check into a pass.','',
    '| New file | Bytes | SHA-256 |','|---|---:|---|']
    for m in v['media']:lines.append(f"| {m['file']} | {m['bytes']} | `{m['sha256']}` |")
    lines += ['',
    f"All {v['protected_files_unchanged']} protected hashes match the start of this revision, including both accepted input videos, SRT, narration, prior report, provenance, download JSON, old explainer/PDF/submission copy, DeepSeek archives and request ledger. Source/application manifests are also protected. Exact hashes are in review/cursor/protected-before.json. Original browser videos remain:",
    '- Clean: `bc4f6f41cafb8da90c42ebf271f196a1894c4f429ad3264560de7b0c936bd7c2`.',
    '- Subtitled: `c005ccba5bfdccb6a6ac90bfc628bd79d04203cd240cdbae1e7cedf244e321d1`.','',
    '## Reproducibility and changes','',
    'New files only: the two cursor MP4s and this report, helpers `review/render_cursor_demo.py`, `review/write_cursor_acceptance.py`, `review/cursor_probe.py`, and evidence/QA files under `review/cursor/`. Private overlay/cache and rejected attempts remain under `.local/cursor-overlay/` and `.local/cursor-review/`. No app/scientific source code, dependency lock, accepted media, PDF, narration or submission copy was edited.','',
    'The renderer decodes each accepted video to bounded RGB frames, composites the sparse transparent overlay on the scheduled frame numbers, and writes exactly one output frame per input frame. New H.264 encoding uses CRF 14. An explicit limited-range flag is then set using `h264_metadata=video_full_range_flag=0` with stream copy: this changes range signaling without another image encode. This introduces ordinary codec/color-conversion rounding, not a pixel-identical video copy; scientific text/value readability was checked in the final decoded images. There is no retiming, new crop, new zoom or UI replacement.','',
    'Two preliminary sparse-image FFmpeg pipelines failed with `Cannot allocate memory` while filtering. Windows commit usage was observed at 96%. Those outputs were not accepted. A static row-2 cue was also rejected when its source-state check found it would point to another row after scrolling; static B/C highlights were corrected for content reflow. These draft videos remain private and are not the deliverables. The final one-frame-at-a-time pipeline limits decoder/encoder threads, passes only bounded frame buffers, and completed both encodes and full decodes. No unrelated application was stopped or system setting changed.','',
    'Run from `D:\\workshop\\oct\\oxyproof-osi-2026`:',
    '```powershell',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/render_cursor_demo.py prepare',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/render_cursor_demo.py render',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/render_cursor_demo.py verify',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/write_cursor_acceptance.py',
    '```','',
    'Final render and verification commands completed with exit 0. Render refuses to overwrite existing destination MP4s. Preparation checks the preserved IAB manifest hashes, maps only validated targets, and caches deterministic transparent annotations. Verification probes dimensions/fps/frame count/duration/audio, fully decodes both videos, checks checkbox state changes, checks every annotation against the subtitle area, and compares all protected hashes. Its actual JSON is `review/cursor/verification.json`; manual visual evidence is `visual-review.json`.','',
    'Application regression tests were NOT RUN because this is a media-only annotation change. No new IAB recording, DeepSeek/OpenAI/Ollama call, application execution, commit, push, upload, publication, deployment or submission occurred. Current checkout began at `816fc06328561f82f0656bf20cd8a60ef31cc3c0`; no Git mutation was performed.','',
    'The next action is owner review and separate English narration. Public actions remain outside the authorized task.','']
    (OUT/'CURSOR_VISUALIZATION_ACCEPTANCE.md').write_text('\n'.join(lines),encoding='utf-8')
    print('CURSOR_VISUALIZATION_ACCEPTANCE_WRITTEN',len(lines),'lines')
if __name__=='__main__':main()
