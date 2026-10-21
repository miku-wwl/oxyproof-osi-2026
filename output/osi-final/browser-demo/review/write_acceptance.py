"""Build the owner's video handover from recorded, local evidence only."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def clock(t):
    m,s=divmod(t,60);return f'{int(m):02}:{s:06.3f}'

def main():
    p=read(OUT/'review/recording-provenance.json')
    v=read(OUT/'review/verification.json')
    b=read(OUT/'review/browser-playback.json')
    lines=['# OxyProof — browser-operation video acceptance','',
    'SPRINT_STATUS=PARTIAL',
    'BROWSER_OPERATION_VISIBILITY=PASS',
    'FULLSCREEN_APPLICATION_PRESENTATION=PASS',
    'SLIDER_INTERACTION=PASS',
    'DEEPSEEK_REPLAY=PASS',
    'JSON_EXPORT=PASS',
    'IAB_SKILL_EXECUTION=PASS',
    'MEDIA_TECHNICAL_VALIDATION=PASS',
    f"BROWSER_PLAYBACK_STATUS={b['status']}",
    'REAL_CURSOR_VISIBILITY=UNAVAILABLE',
    'NATIVE_BROWSER_WINDOW_CHROME=UNAVAILABLE','',
    '**Overall acceptance is PARTIAL.** The IAB screenshot API does not capture the real system pointer or native address bar/window chrome. This is genuine webpage viewport footage. No cursor, pointer trail, click animation, UI result or scientific output was fabricated. The six named gates above concern the verified operations and application presentation; they do not waive the separate real-cursor requirement.','',
    '## Deliverables and presentation','',
    'Both MP4s are 03:15 (195.000 seconds), 1920×1080, H.264 High Level 4.0, yuv420p, 30 fps / 5,850 frames, TV range, faststart, with no audio. The clean edition has no narration subtitles. Both have only a brief final GitHub URL over the actual dashboard at 03:12–03:15. There is no opening title card, permanent title banner, editorial commentary rail or decorative frame. The native OxyProof navigation sidebar belongs to the actual application.','',
    'The clean video fills the canvas with the genuine webpage. Minimal caption strips are 84/1080 pixels high, leaving at least 92.22% unobscured application in the subtitled edition (the JSON viewer occupies the evidence-inspection scene). Source frames are 1921×1081, including unused capture-interface padding. The inspected full webpage rectangle is 1749×984 at [0,0,1749,984]; resizing to the output is approximately 1.098×. This is **not native 1080p or native 30-fps capture**. The same real operations and timing underlie both editions.','',
    'The SRT contains 25 short English action cues, not a verbatim transcript. The narration is 369 words, aligned to seven actual sections; owner voice recording is pending. Both supplied video masters are intentionally silent.','',
    '## IAB skill execution and source handling','',
    'The actual installed skill was read and executed: `C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md`. Its internal ID is `codex-iab-video-recording`; its display name is **IAB Browser Video**. These names identify the same installation.','',
    'The skill `capture_iab.mjs` recorded timestamped genuine captures concurrently with actual UI actions in the selected ChatGPT IAB (browser 2 / application tab 1). Its `render_iab.py` was run for the successful 8-second preflight and complete decode/visual inspection. The production renderer uses the verified source hashes and timestamps, preserving actual duration at 1× speed. It adds only padding removal, output scaling, minimal captions and the final supplied GitHub URL. No external browser, Windows desktop control, OBS or synthetic UI was used.','',
    'The previous explainer and original full-resolution frames were reviewed first. Fresh capture was necessary for the complete current selection → Analyze → slider → B/C replay → download → JSON-viewer chain. Previous media, raw captures, accepted PDF and submission copy are preserved. Private raw captures remain under `.local/browser-demo-capture/`; they are not bundled as public material.','',
    'Eight accepted takes are joined in original scene order, with necessary cuts between scenes and no speed-up. The original closing navigation take F included a transient loading frame and changed capture dimensions. It remains preserved but is excluded; F-ready shows the genuine ready dashboard after that navigation. The initial incorrect-coordinate preflight did not establish slider movement and was excluded; the successful native-drag preflight and the final three actual drags establish it.','',
    '| Take | Final interval | Actual acquisition fps | Maximum sample gap (s) | Frames used |','|---|---|---:|---:|---:|']
    for t in p['takes']:
        a,z=t['video_interval_s'];lines.append(f"| {t['take']} | {clock(a)}–{clock(z)} | {t['capture_average_fps']:.3f} | {t['max_sample_gap_s']:.3f} | {t['source_frames_used']} |")
    lines += ['',
    'The capture target was 15 fps; source acquisition varies with IAB latency. The largest 1.836-second gap occurs during E navigation to the JSON viewer. Repeated frames at 30-fps export preserve elapsed time and do not add motion detail.','',
    '## Timestamped actual operations','',
    'Times below are the recorded action request and completion mapped into the final video, rather than merely planned timings. Readability holds and resulting states are visible after completion. Source manifests and frame hashes are linked in `review/recording-provenance.json`.','',
    '| Take | Actual action | Requested | Completed |','|---|---|---:|---:|']
    for a in p['actions']:
        lines.append(f"| {a['take']} | {a['action']} | {clock(a['video_request_s'])} | {clock(a['video_complete_s'])} |")
    lines += ['',
    'The three final native IAB drags changed the real slider indices 0 → 31 → 60 → 92. At 700 K the visible order is 1 > 2 > 3; at 1000 K it is 3 > 2 > 1. The interaction proof contains observed bounds, actual drag coordinates and before/after values, not a drawn cursor. The approximate model crossings are displayed and read at 01:19–01:35.','',
    'Replay controls are visibly operated, including Load recorded DeepSeek traces, Replay B and Replay C. B shows `analyze_temperature_interval`, validated 700–1000 K / rows 1,2,3 and the independent audit. C shows the original humidity and 10,000-hour question, model proposal, `BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR`, no executed scientific tool and zero candidates.','',
    'The actual Export JSON click completed at 02:58.136. The real download is 141,505 bytes. The local viewer displays a byte-identical copy, with SHA-256 `190430d6355326281c501057df5a2167782209768ad88ddd62fd66bad29e224c`. The viewer is visible after the navigation beginning at 03:02.013; the action wrapper completed at 03:07.168. The source frames visibly contain JSON before that wrapper completion. This is a verified local representation expressly allowed by the request.','',
    '## Scientific claims checked against the recorded export','',
    'No article, event page, license or dataset was freshly re-fetched during this video-only revision. Scientific claims were checked against the pinned local real dataset, previously verified provenance and saved independent 80-digit decimal reference in `artifacts/scientific_acceptance.json`. This is a numerical cross-check of the actual new export, not a newly executed experimental validation.','',
    '- Dataset: [Jang et al. / Zenodo 18947543](https://zenodo.org/records/18947543), DOI `10.5281/zenodo.18947543`, 483 records, CC BY 4.0; source access date recorded as 2026-10-20. Dataset SHA-256: `8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34`.',
    '- Dataset publication: [Charting the Landscape of Oxygen Ion Conductors](https://www.nature.com/articles/s41597-026-07100-x).',
    '- Original comparable source: [Huang et al., J. Am. Ceram. Soc. (1998)](https://doi.org/10.1111/j.1151-2916.1998.tb02662.x), rows 1–3, bulk, two-probe AC, reported 600–1100 K. These are curated source parameters; original full methods/sample conditions remain unverified.',
    '- Formula: sigma = A/T × exp(−Ea/(kB×T)); activation energy meV → eV, prefactor K S/cm, temperature K, conductivity S/cm. All six endpoint values in the downloaded report match the saved independent decimal reference within relative tolerance 1e-12.',
    '- Fixed-regime model roots: 776.4074250510221 K, 817.9098253678244 K and 854.261466339589 K; they match the saved analytic/decimal reference within 1e-9 K. They are calculated intersections, not observed transition measurements. Published fit boundaries are separate; exact T-star results are withheld and ±5 K is an engineering review heuristic, not uncertainty.',
    '- Ranking is conditional within the comparable source group. Atmosphere, preparation, density, sample uncertainty and humidity/lifetime validation are missing. No new material, experiment or uncertainty interval is claimed.',
    '- Recorded genuine DeepSeek executions are historical: B response `8555b7b9-84f2-4553-b7ec-0041482bc9aa`; C response `36ab33a0-d258-4190-a5d4-4d867fd4fe0f`. The source archives and three-request budget ledger are unchanged. Current analysis and export are `OFFLINE_DETERMINISTIC`; replay is explicitly labeled historical and makes zero new inference requests.','',
    '## Verification and actual playback','',
    f"Technical/evidence verification completed at {v['verified_at_utc']}. **PASS** applies to the checks below, not to unmet cursor or continuous-browser-playback requirements.",'']
    lines += [f'- {c}.' for c in v['checks']]
    lines += ['',
    '35 actual decoded final frames and a contact sheet were inspected, including the selection and Analyze states, 700/1000 K orders, intermediate slider positions, all three crossings, B tool/arguments, C abstention, source rows/DOI, export, downloaded JSON and final GitHub URL. No blue text-selection artifact, unwanted blank padding, sidebar template or synthetic cursor was accepted. The primary results are readable at full-size 1920×1080.','',
    f"**IAB playback: {b['status']}.** {b['summary']}",'',
    'The initial QA extractor failed once in FFmpeg and then with Windows `WinError 1455` (page file too small). It was changed to a single decoder process with bounded threads; the final verification command completed with exit code 0. The first render correctly rejected transient mismatched dimensions in F; the corrected accepted F-ready take passed. These failed attempts were not counted as passes.','',
    '| File | Bytes | SHA-256 |','|---|---:|---|']
    for m in v['media']:lines.append(f"| {m['file']} | {m['bytes']} | `{m['sha256']}` |")
    lines += ['',
    '## Changed files and run commands','',
    'Only the new `output/osi-final/browser-demo/` namespace and private `.local/browser-demo-capture/` / `.local/browser-demo-render/` working assets were created. Product source code, scientific algorithms, dependency locks, historical acceptance records, PDF, submission copy and old explainer videos were not changed. Git HEAD remains `4286620b13f57c5a5f30af9e00302b0c19259b07`; no commit, push, deployment, upload or submission occurred.','',
    'Primary files: `oxyproof-browser-demo-clean.mp4`, `oxyproof-browser-demo-subtitled.mp4`, `oxyproof-browser-demo.srt`, `BROWSER_DEMO_NARRATION.md`, `BROWSER_DEMO_ACCEPTANCE.md`. Supporting review files include the production/validation/report scripts, PLAYER.html, JSON export/proofs, protected hashes, acquisition provenance, verification.json, browser-playback.json and screenshots.','',
    'Run from `D:\\workshop\\oct\\oxyproof-osi-2026`:','',
    '```powershell',
    '# Verification: actually executed, exit 0',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/validate_browser_demo.py',
    '# Rebuild acceptance from saved evidence',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/write_acceptance.py',
    '# Local review server; the existing instance already listens on 127.0.0.1:8017',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/review/scripts/serve_review.py --port 8017',
    '# Production render: already executed; refuses to overwrite existing MP4s',
    '.\\.local\\pdf-venv\\Scripts\\python.exe output/osi-final/browser-demo/review/produce_browser_demo.py',
    '```','',
    'Review URL: http://127.0.0.1:8017/browser-demo/review/PLAYER.html. The real repository URL in the closing overlay is https://github.com/miku-wwl/oxyproof-osi-2026 (also matches local origin).','',
    'Backend/frontend regression tests were **NOT RUN** in this media-only revision; no product changes were made. Historical test counts are not presented as current results. The actual new verification is the media/evidence command above.','',
    '## Remaining limits and next actions','',
    '1. Full acceptance still requires a recording capability that captures the real system pointer while respecting the owner’s IAB-only boundary. The present documented API exposes no such capability. Do not add an artificial pointer to claim completion.',
    '2. Native browser chrome/address bar is absent; the delivered footage captures the genuine webpage viewport. Browser continuous-playback evidence is limited exactly as stated above.',
    '3. Record owner narration if desired; the requested clean and subtitled masters remain silent.',
    '4. Human review/submission remains outside this revision. No public action is authorized or performed.','']
    (OUT/'BROWSER_DEMO_ACCEPTANCE.md').write_text('\n'.join(lines),encoding='utf-8')
    print('WROTE BROWSER_DEMO_ACCEPTANCE.md',len(p['actions']),'timestamped actions')

if __name__=='__main__':main()
