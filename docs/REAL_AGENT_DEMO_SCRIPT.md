# Phase 2.6 research-agent demonstration

**Phase 2.6.1 update:** the offline steps remain valid; local Ollama native acceptance failed. See [current demo gate](OLLAMA_AGENT_DEMO.md). The zero-call statements below describe the historical Phase 2.6 execution, not the later three local inference requests. No successful live-model footage exists.

Prepared October 21, 2026 NZDT. **Current mode: OFFLINE_DETERMINISTIC; live model NOT_CONFIGURED, zero real calls.** Do not describe the current demonstration as successful live AI planning. The model adapter and contracts are implemented; genuine live acceptance remains outstanding.

Start with verified dependencies/assets/data present:

```sh
python scripts/start.py --offline
```

Open http://127.0.0.1:8000. A fresh owned service is running there at handover. For initial setup use `python scripts/start.py`. Stop an owned existing server before starting a second one on the same port.

| Step | Action | Evidence / judge explanation |
| --- | --- | --- |
| 1 | Find **Research Agent execution**; show runtime and provider status | Offline grammar is clearly labelled; no model call implied before execution. Three allowlisted scientific tools, independent evidence guards. |
| 2 | Choose **Screening question**, keep rows 1,2,3, run | Exact natural question, nominal 600 C / 873.15 K. Expand validated arguments and scientific result for S/cm values and source groups. Row 3 uses LT here, not HT. Promising means conditional in-source screening, not a guarantee. |
| 3 | Review the seven-part trace and export Agent JSON | Question, runtime/model identity, selected tool, validated args, result, audit and grounded explanation. No model identity in offline mode; numbers/citations come from the backend. |
| 4 | Choose **Huang interval question**, clear row IDs, run | The explicit named demo resolves only published rows 1-3. Tool is interval analysis. Explain 700 K order 1>2>3 vs 1000 K 3>2>1 using the displayed curated Ea values, prefactor ratios and valid regimes. |
| 5 | Expand scientific result; optionally use original Temperature Decision Explorer flagship | Three continuous roots differ from published T*. Approximately 776/818/854 K are model crossings; uncertainty bounds unavailable; experimental confirmation required. The Explorer now also has a backend execution-trace accordion. |
| 6 | Choose **Humidity and lifetime question**, run | Both 10% humidity and 10,000 operating hours remain in the refusal. ABSTAINED / UNVERIFIED_CONSTRAINTS, no complete recommendation. Proposed exposure/durability evidence has not been measured. |
| 7 | If desired with current unconfigured environment, choose REAL_LLM and run | Explicit 503 UNAVAILABLE / NOT_CONFIGURED, no fabricated trace and no automatic offline success. Select offline explicitly for another run. This illustrates failure handling, not live integration. |

For a **future authorized live demo**, configure OPENAI_API_KEY and OXYPROOF_LLM_MODEL through the environment and restart the API to inherit them. First run the bounded acceptance CLI described in `REAL_AGENT_ACCEPTANCE.md`. Only when actual checks pass should the UI be shown as genuine provider planning. Select REAL_LLM, run A/B/C once, show real model/response identity and MODEL_SELECTED tool, then inspect independent scientific results. Do not repeatedly click or exceed the approved request budget. Stop and record provider failures without substituting a mock.

Reproduce current permitted acceptance and full regression:

```sh
uv run --offline --no-sync python scripts/accept_real_agent.py
uv run --offline --no-sync python scripts/validate_v2.py --browser --phase26
uv run --offline --no-sync python scripts/phase2_demo.py
```

Public claims allowed now: actual published-data offline screening, analytic rank reversal, evidence refusal, tested bounded planner/adapter contracts and real local browser execution. Not allowed: live-model success, experimental discovery, measured crossings, verified humidity/lifetime, general 100% accuracy or competition submission. The 49-case benchmark is targeted and partly synthetic. Current screenshots are in `artifacts/browser/agent-*.png`; prior video/PDF remain historical preserved assets, not newly recorded live-agent footage.
