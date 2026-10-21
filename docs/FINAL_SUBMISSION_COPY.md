# OxyProof: When the Best Material Changes, Can Your AI Explain Why?

**A temperature-aware, evidence-grounded materials decision agent**

Selecting an oxygen-ion conductor at one temperature can hide a change in the defensible choice across an operating range. Researchers also need to know whether measurements are comparable and whether an AI has silently ignored a requirement. OxyProof makes those decisions inspectable.

The local Python API and React dashboard combine three bounded tools: screening, temperature-interval analysis and source-row evidence inspection. Independent checks enforce units, measured ranges, fitted regimes and provisional source groups. Unsupported requirements produce a typed abstention. Deterministic calculations and templates control every scientific number and citation; unrestricted model prose cannot introduce evidence. OFFLINE_DETERMINISTIC is explicitly a bounded grammar/state machine. Optional OpenAI planning is implemented and contract-tested, but no live model call has been verified.

The demonstration uses Jang et al.'s published 483-record dataset, not invented materials. Three bulk records attributed to Huang et al. change calculated order from rows **1 > 2 > 3 at 700 K** to **3 > 2 > 1 at 1000 K**. The reason is the interaction of prefactors, activation energies and temperature regimes. Analytical crossings near **776, 818 and 854 K** lie within joint fixed-regime evidence. They remain separate from curated T* boundaries, where the affected row is withheld.

**Model-derived crossover temperatures; uncertainty bounds unavailable; experimental confirmation required.** Shared source, method, conductivity type and range permit conditional screening, not experimental superiority. The original article's abstract and identity were checked; its full methods/Table 3 and row-specific atmosphere, preparation, density and uncertainty were not independently verified. Humidity tolerance and long-term stability cannot be established.

The workbench also rejects a humidity requirement and demonstrates why reusing this dataset's prefactor without 1/T fails dimensional consistency. JSON export preserves source IDs, original parameter strings, units, regimes, evidence limits and code fingerprints. This integrated decision audit is the contribution; no new material or experimental phenomenon is claimed.

Validation passed **145 backend tests, 8 component tests and 14 genuine Chromium browser checks**. It also passed **49 targeted scientific integrity cases, including adversarial constraints and model-boundary checks**. That selected, partly synthetic corpus does not establish general accuracy. Independent Decimal/SI calculations verify the three roots and ordering on either side. Pinned dependencies, a checksum-verified full CSV and an attributed 24-row fixture support offline reproduction.

OxyProof can help researchers identify decisions worth checking and the missing evidence that matters next. Follow-up work should verify original sample conditions and measure near predicted crossings, with uncertainty reporting. No autonomous experiment, device-performance guarantee or live LLM result is claimed.

Sources: [Jang et al., dataset v1, CC BY 4.0](https://doi.org/10.5281/zenodo.18947543); [dataset methodology](https://www.nature.com/articles/s41597-026-07100-x); [Huang et al., 1998](https://doi.org/10.1111/j.1151-2916.1998.tb02662.x).

Repository: https://github.com/miku-wwl/oxyproof-osi-2026. Release candidate remains local pending approval. Development began October 20, 2026; organizer confirmation of pre-event eligibility is outstanding. Prepared for owner review; not submitted.
