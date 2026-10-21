# Third-party rights

The MIT software license applies to original OxyProof code, added in Phase 2 at the owner's request. It does not relicense scientific sources or dependency packages.

The unchanged published-data fixture is CC BY 4.0: Jang, Seong-Hoon; Kiyohara, Shin; Takamura, Hitoshi; Kumagai, Yu (2026), *Charting the Landscape of Oxygen Ion Conductors: A 60-Year Dataset*, Zenodo, https://doi.org/10.5281/zenodo.18947543. Original indices, field names, fixture selection and checksum are in `backend/app/data/fixtures/manifest.json`. Selection and encoding are the only fixture modifications.

The Nature article has separate rights (CC BY-NC-ND 4.0 per the first sprint's direct source inspection). No article figures or article text are redistributed. Original source paper DOIs remain citations, not a grant of rights over those papers.

Installed third-party Python and npm packages retain their own license files. Exact versions are in `uv.lock` and `frontend/package-lock.json`; the application does not claim ownership of those dependencies. No third-party media, music, external fonts or stock figures are bundled.

Final acceptance inventory: `artifacts/license_inventory.json` records 30 installed Python distributions and 271 installed npm lock entries, with license metadata/files. Optional PDF-rendering tools live in a separate ignored environment. `THIRD_PARTY_RUNTIME_LICENSES.txt` preserves the notices for React, React DOM, Scheduler and Lucide used by the frontend bundle. It must accompany any future distribution of built assets. No dependency is relicensed by OxyProof.
