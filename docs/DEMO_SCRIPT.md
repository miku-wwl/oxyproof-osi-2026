# Local judge demonstration (target: about 3 minutes; not a recorded video)

Pitch: **OxyProof turns published oxygen-ion conductivity parameters into checkable screening decisions, and shows when a number should not be trusted.**

Start from the repository root: `python scripts/start.py --offline` after setup. Open http://127.0.0.1:8000. The page begins without preloaded candidate values. Confirm `OFFLINE_DETERMINISTIC`, the loaded row count and full-data/subset badge. All scientific results come from FastAPI.

1. **0:00–0:40 — The question.** Click **600 °C screening**. It selects published source rows 1, 2 and 3. Explain that these are compositions/conditions in a curated experimental dataset, not newly discovered compounds. At 873.15 K their regimes are determined individually.
2. **0:40–1:20 — The calculation and evidence.** Show the group ranking (rows 3, 2, 1 at this temperature), bar comparison, and the exact DOI/method/range. Open row 1: the engine selects HT, Ea=634 meV, A=52785.93227 K·S/cm, giving sigma ≈0.013243811986442925 S/cm. The temperature curve draws only supported intervals and splits at regime changes. These are model-derived values, not point measurements.
3. **1:20–1:55 — A seductive wrong answer.** Click **Wrong-formula audit**, then inspect **Challenge the formula**. Omitting 1/T with the same A gives approximately 11.563834436 **K·S/cm**, which is not conductivity; its ratio to the correct quantity is 873.15 **K**. Use the API's exact returned number, not this rounded narration. This demonstration is about the dataset's convention, not an accusation against a particular paper.
4. **1:55–2:25 — Abstain usefully.** Click **Unresolved regime** (real row 462). Both unknown conductivity type and missing T* are preserved. No ranking is shown. Click **Outside measured range** (real row 39 at 600 °C); its reported interval is 1000–1300 K, so default calculation is withheld. If explicitly allowing extrapolation, it stays unranked.
5. **2:25–3:00 — Leave an audit trail.** Re-run the baseline. Export JSON and inspect dataset DOI, checksum, original one-based row, raw source strings, units, equation, code fingerprint, warning codes and trace. Show the next-measurement advice is labelled heuristic and no experiment was run.

## Three reproducible published-data cases

`uv run --offline --no-sync python scripts/demo.py` writes all three normal cases and two abstention cases:

| Artifact | Published rows | Target | Expected |
| --- | --- | --- | --- |
| `artifacts/600c_huang_bulk.json` | 1, 2, 3; Huang et al., 1998 | 600 °C | Three conditional in-group calculations |
| `artifacts/827c_cobalt_bulk.json` | 39; source DOI 10.1016/S0167-2738(00)00770-0 | 1100 K | One in-range bulk calculation |
| `artifacts/327c_bismuth_bulk.json` | 483; source DOI 10.1016/0025-5408(89)90164-5 | 600 K | One in-range bulk calculation |

Use the exact Kelvin temperatures for the latter two: artifact filenames round the Celsius labels. The CLI demonstration uses the portable 24-row published fixture deliberately, so its artifact source scope is independent of the local full-file cache.

## Runtime boundary

No paid key is required. REAL_LLM is a separately selected, single-call structured tool-plan adapter, currently NOT_CONFIGURED. It has only transport contract tests, not a verified live model output. Browser E2E was NOT RUN: the available computer/browser tool reported no browsers. HTTP API, component contracts and production build have separate verification evidence in `VALIDATION.md`.
