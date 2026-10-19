# Engineering decisions

- Preserve the clean initial repository (base a2ad59c5bc923275584497d42f5ebc7977e1217f). No commits or remote changes.
- Complete source inspection before implementing science; verified dataset-specific units differ from a naive eV or molar-energy assumption.
- Python 3.12+ / uv / FastAPI / Pydantic; pandas only for data inspection. Standard-library log-domain arithmetic avoids unnecessary scientific infrastructure.
- React/TypeScript/Vite UI; locally computed SVG plots from API data; no hosted services, fonts or chart CDNs.
- Bundle a small attributed, unchanged-field published subset with original row IDs. Download the pinned full file at bootstrap; both modes are explicitly identified.
- Deterministic, bounded orchestration with a visible trace; optional one-call, allowlisted typed LLM plan. No autonomous shell, generated-code execution or arbitrary URL fetching.
- Treat incomplete regime metadata as evidence insufficiency; separate bulk, total and unknown types; no global league table across different experiments.
- Source-tree fingerprint in each report identifies uncommitted calculation code, in addition to the base Git SHA. Deterministic outputs omit wall-clock timestamps and random IDs.
- Honest validation boundaries: mocked transport is permitted only in adapter contract tests; a passing mock test cannot verify REAL_LLM.
# Phase 2 decisions

- Independent span coverage replaces keyword-only rejection. REAL_LLM remains constrained by the same grammar to avoid delegating completeness to a single model. Accepted phrasing is intentionally narrower than general English.
- Structured-only API temperatures do not inherit an invented 600 C goal. Guided UI text is generated from controls; manual text is preserved until explicitly reset.
- Fixed-regime pair intersections and analytic roots drive the interval map, not plot samples. A published fit boundary has a different event type from a continuous root; T* is never bridged.
- Three allowlisted tools share deterministic validation and template explanations. Provider text is never a scientific source. No live credentials/model were available; contract tests remain labelled mocks.
- Original code uses MIT at the owner's Phase 2 request. Dataset CC BY 4.0 and article rights remain separate. Browser binaries, source HTML and large local media stay in ignored `.local`.
- Chromium/FFmpeg installation is project-local on D:. Genuine browser tests launch their own port-8011 server and do not reuse an unrelated/stale service. No global settings or public endpoints were changed.
