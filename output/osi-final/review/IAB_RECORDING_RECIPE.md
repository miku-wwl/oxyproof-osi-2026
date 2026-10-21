# Reproduce the genuine browser capture

This records the existing OxyProof app; it does not create a new app or invoke a model. The actual installed skill and complete helper documentation are at `C:/Users/weila/.codex/skills/codex-iab-video-recording/`.

1. Read its SKILL.md and current browser-tool documentation. Inventory the current browser, verify `type=iab`, bind or open the owner-selected local app tab, and observe the actual DOM. Do not blindly reuse this run's browser 2/tab 1 IDs.
2. Keep provider access disabled; load the existing full pinned dataset or labelled fixture. Use the flagship rows 1/2/3 preset. Do not press a fresh REAL_LLM run, reset the budget or change credentials.
3. Apply a 1600 x 900 recording viewport through the documented capability; verify actual acquired dimensions before each take. This session produced 1441 x 811 screenshots. If the visible IAB is resized, recheck source dimensions and readability.
4. Dynamically import the installed sampler **inside the browser-capable REPL**, not a separate Node process:

```javascript
let capture = await import('file:///C:/Users/weila/.codex/skills/codex-iab-video-recording/scripts/capture_iab.mjs');
let take = await capture.recordIabTake({
  tab, browserId: observedIabId,
  outputDir: 'D:/workshop/oct/oxyproof-osi-2026/.local/new-review-take',
  seconds: 8, targetFps: 15, label: 'real-temperature-change',
  steps: [{at:2,label:'show-1000K',run:async c=>{
    await c.click(tab.playwright.getByRole('button',{name:'1000 K',exact:true}),'1000K');
  }}]
});
nodeRepl.write(take);
```

The control name above was actually observed in this run; observe it again before a new run. Keep sampler and scheduled UI actions in the same awaited call, new private directories, and timeout margin. Preserve the generated frame files, hashes, timestamps and manifest. Perform the 5-8 second preflight encode/decode/view first using the skill renderer.

| Accepted take | Seconds | Genuine actions/state |
| --- | ---: | --- |
| scene1 | 25 | Dashboard, loaded scope, Temperature Decision Explorer; top-of-page state |
| scene2a | 35 | Begin full curves at 700 K; at 7 s click 700 K; at 15 s press ArrowRight on `Decision temperature slider` 12 times; at 24 s click 1000 K |
| scene2b | 25 | At 1/8/14/20 s click observed event headings for approximately 776/818/854/875 K; last is a fit boundary |
| scene3a | 10 | Expand recorded acceptance before capture; at 2 s click `Load recorded DeepSeek traces`; default A is identified by the app |
| scene3b | 35 | At 1 s `Replay B`; 5 s `2 · Planning and model`; 15 s expand `4 · Validated tool arguments`; 23 s expand `5 · Scientific execution result`; 29 s `6 · Evidence audit:` |
| scene4-final | 40 | Already-replayed C with question visible; 14 s `3 · Scientific tool`; 23 s scroll down 0.25 page; 31 s `7 · Grounded explanation` |
| scene5-final | 30 | Expanded original-provenance section with row 2 centered and all three records visible; at 12 s scroll down 0.16 page; at 22 s wait for download and click `Export decision JSON` |

The original capture also contains the actual `Replay C` button action; final C footage reuses that read-only result at a consistent size. Download verification used `tab.playwright.waitForEvent('download')` before clicking; the returned path was parsed and checked against the exported report. No success display was fabricated.

The private manifests are the authoritative actual timings; scheduled action times are requests, not claims of instantaneous UI response. The media script validates hashes, trims at whole seconds, preserves 1x sampling intervals, creates editorial header/rail labels and adds the 15-second closing card. A standalone review package excludes private raw frames; the owner should retain `.local/osi-final-capture/` for future edits.
