# OxyProof: When the Best Material Changes, Can Your AI Explain Why?

**A Temperature-Aware, Evidence-Grounded Materials Decision Agent**

Selecting an oxygen-ion conductor at a single temperature can conceal a change in the defensible choice across a device's operating range. OxyProof combines a local research workbench with bounded scientific tools to expose those changes and the evidence needed to justify them.

We build on the published Jang et al. dataset ([Zenodo v1](https://doi.org/10.5281/zenodo.18947543), CC BY 4.0): 483 experimental-fit records, not 483 unique formulas. Our contribution is an auditable decision workflow, not discovery of the fitted parameters or correction of the source literature. A strict planner selects screening, interval analysis or evidence inspection. Deterministic tools enforce units, measurement ranges, regimes and source-group comparability; generated explanations cannot introduce model arithmetic or invented citations. Offline mode is explicitly a deterministic grammar/state machine. Optional OpenAI tool planning is implemented and contract-tested but has not been live-verified without credentials.

For three bulk records from [one experimental report](https://doi.org/10.1111/j.1151-2916.1998.tb02662.x), calculated ordering changes from rows 1 > 2 > 3 at 700 K to 3 > 2 > 1 at 1000 K. The dashboard shows original chemical formulas, curves and interval ranks. Analytic roots are accepted only inside both measured, fixed-regime intervals. Published T* changes remain distinct from continuous model crossings; exact transitions are withheld. These are model-based screening results, not new observations or experimental guarantees.

The agent rejects a humidity-stability request because this dataset cannot verify it. An educational wrong-formula challenge rejects reuse of the same prefactor without 1/T on dimensional grounds. Exported JSON preserves source DOIs, original rows/parameters, units, regimes, warnings, verdicts and a code fingerprint.

Reproducibility includes pinned dependencies, full-file checksum/schema validation, an attributed 24-row offline fixture, independent Decimal/SI references, real browser/API testing and a 49-case hand-selected decision-integrity benchmark. These checks do not establish general scientific accuracy, statistical significance or experimental validation. Missing atmosphere, preparation, density and uncertainty require original-source review and follow-up measurements.

Repository: https://github.com/miku-wwl/oxyproof-osi-2026. Phase 2 is local until owner-approved publication. Development began October 20, before the October 21–22 event; eligibility and current Slack submission instructions still require organizer confirmation. This is a concise text draft, not a verified typeset one-page PDF.
