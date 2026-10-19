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
