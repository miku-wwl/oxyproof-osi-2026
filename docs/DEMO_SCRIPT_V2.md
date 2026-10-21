# OxyProof: When the Best Material Changes, Can Your AI Explain Why?

Target: 3–4 minutes. Use a fresh browser at the local API root. Select OFFLINE_DETERMINISTIC; show the actual loaded dataset scope. No recording is implied by this script; the handover reports separately whether a capture was produced and inspected.

| Approx. time | Action | Judge-facing explanation |
| --- | --- | --- |
| 0:00–0:20 | Show research workbench and dataset attribution | A choice at one operating temperature does not establish the choice across a device's range. OxyProof audits the decision, not just a number. |
| 0:20–1:10 | Click “Published rank reversal · rows 1 / 2 / 3”; show curves, 700 K then 1000 K | Same report, bulk, two-probe AC, 600–1100 K. Actual formulas are visible. At 700 K the model order is 1 > 2 > 3; at 1000 K, 3 > 2 > 1. These are published-fit computations. |
| 1:10–1:50 | Inspect analytic roots and a published T* event | Three valid continuous model crossings are distinct from changes in selected fit. Exact T* is withheld; ±5 K is a review heuristic, not uncertainty. No assumption that fitted branches join continuously. |
| 1:50–2:20 | Click Wrong-formula audit | Reusing this dataset's A without 1/T has units K S/cm. This is an educational dimensional counterexample, not proof of a specific paper error. |
| 2:20–2:55 | Ask “Find bulk conductors at 600 C that survive 10% humidity”; run; open warnings | UNVERIFIED_CONSTRAINTS. The requirement cannot be silently dropped. Show the proposed controlled-humidity conductivity/stability measurement; no experiment was run. |
| 2:55–3:40 | Inspect formulas/parameters/provenance; export decision JSON | DOI, raw row IDs, units, selected regimes, evidence bounds, warnings and code fingerprint survive export. Real science works offline. REAL_LLM remains visibly optional and not live-verified. |

Research interpretation: ordering reverses because prefactor ratios and activation-energy differences interact with temperature and selected regimes. The common source and fitted ranges support a conditional comparison. Atmosphere, preparation, density and parameter uncertainty remain unverified. Re-measure near predicted roots and T*, retaining bulk/grain-boundary separation. No new material was discovered.

Final acceptance qualification: **Model-derived crossover temperatures; uncertainty bounds unavailable; experimental confirmation required.** Public crossing captions use approximately 776, 818 and 854 K; full numeric coordinates survive technical JSON. The original abstract and bibliographic record were inspected in Phase 2.5; full original methods/Table 3 remain unverified. The accepted updated video is separate under `.local/demo-phase25/`; the original recording is preserved.

Reproduce data artifacts: `uv run --offline --no-sync python scripts/phase2_demo.py`. Genuine browser capture: `uv run --offline --no-sync python scripts/browser_e2e.py --record` after building assets and installing Chromium. The capture uses live local API results and clearly identified caption overlays; no voice, fabricated model responses or external article figures.
