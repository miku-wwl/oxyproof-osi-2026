# OxyProof: When the Best Material Changes, Can Your AI Explain Why?

**A temperature-aware, evidence-grounded materials decision agent.** OxyProof combines published data, bounded AI tool selection, deterministic physics and independent auditing to explain when a preferred material changes with temperature, and when the evidence cannot support a recommendation.

Selecting an oxygen-ion conductor at one temperature can hide a different decision across an operating range. Researchers also need to know whether observations are comparable and whether an AI has silently dropped a requirement. OxyProof makes those decisions inspectable through a local FastAPI and React research workbench.

The flagship example uses three curated bulk-conductivity records attributed to Huang et al. within Jang et al.'s published **483-record dataset**. Their conditional model ordering changes from **rows 1 > 2 > 3 at 700 K** to **3 > 2 > 1 at 1000 K**. Analytical intersections near **776, 818 and 854 K** arise from activation-energy differences and prefactor ratios within valid fitted regimes. The calculation uses `sigma = A/T * exp[-Ea/(k_B*T)]`, with explicit units and measured-range checks. Published T* fit boundaries are treated separately; continuity is not presumed and exact T* is withheld.

The language model selects a tool; it does not supply the scientific arithmetic. **DeepSeek/deepseek-flash completed three specific genuine API acceptance scenarios on October 21, 2026**: screening, interval analysis and unsupported-constraint abstention. In the third, the model proposed screening and flagged unsupported requirements; independent validation retained the original 10% humidity and 10,000-hour requirements, prevented scientific execution and returned insufficient evidence with no candidates. The video explicitly replays these saved genuine executions. It makes no new inference request.

Every result carries source rows, parameters, units, selected regimes, warnings and code fingerprints in an exportable JSON report. A pinned CSV checksum, locked dependencies and an attributed 24-row fallback fixture support deterministic offline reproduction. The contribution is an integrated decision audit with bounded tool execution and explicit abstention, rather than a claim that the transport algebra is new.

Retained engineering evidence reports **255 backend, 12 component and 21 Chromium tests passed**, plus **49/49 targeted scientific integrity cases**. The selected, partly synthetic benchmark and three model questions do not establish general accuracy. Independent Decimal/SI calculations verify the showcased roots and endpoint ordering. These are historical project results; this production sprint separately checks the media, exports and archived replay.

**Model-derived intersections, not measured crossovers; uncertainty bounds unavailable.** Shared source/type/method/range supports conditional screening, not experimental equivalence. Original row-specific atmosphere, preparation, density and full methods/Table 3 remain unverified. Humidity stability, lifetime and device performance cannot be established. No new material or experiment is claimed.

Code: https://github.com/miku-wwl/oxyproof-osi-2026  
Data: Jang et al. (2026), Zenodo v1, CC BY 4.0, https://doi.org/10.5281/zenodo.18947543  
Method: https://www.nature.com/articles/s41597-026-07100-x  
Original study: https://doi.org/10.1111/j.1151-2916.1998.tb02662.x  
Demo: **[PUBLIC VIDEO URL - owner upload pending]**

Prepared for owner review; not submitted. The repository is public; these new production assets remain local. Development began October 20. Registration and pre-event eligibility are confirmed by the owner; final submission routing still needs attendee confirmation.
