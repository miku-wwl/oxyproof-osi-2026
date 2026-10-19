# Scientific source register

Access date for this inspection: **2026-10-20 NZDT**. Direct verification means retrieved and inspected, not an independent replication of the original experiments.

| Source | Verification | Use |
| --- | --- | --- |
| Jang, S.-H., Kiyohara, S., Takamura, H. & Kumagai, Y. (2026), https://www.nature.com/articles/s41597-026-07100-x | Direct HTML retrieval succeeded with Python urllib; browser search fetch encountered Nature cookie redirect (500) | Methods equation and curation; Data Records regime semantics |
| https://www.nature.com/articles/s41597-026-07100-x/tables/1 | Direct HTML retrieval succeeded | Ea in **meV**, A in **K·S·cm⁻¹**, high/low regime meaning |
| https://zenodo.org/records/18947543 | Directly retrieved | Dataset publication/attribution |
| https://zenodo.org/api/records/18947543 | Direct JSON retrieval | Version-specific DOI, license, size, MD5 |
| https://zenodo.org/records/18947543/files/oxygen_ion_conductor_dataset.csv?download=1 | Directly downloaded and parsed | 483 rows, 34 columns, 84 distinct source DOIs, 452 distinct Formula strings |
| https://creativecommons.org/licenses/by/4.0/ | Linked license identified by Zenodo metadata `cc-by-4.0` | Dataset attribution and redistribution terms |

Dataset DOI **10.5281/zenodo.18947543**, version index 0 (record 18947543). File length **122657 bytes**; MD5 **45f25ce4ef0240271ee5c35ea75400f1**; SHA-256 **8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34**. Pin the record, not its concept DOI. The importer must reject changed content.

Zenodo explicitly labels the dataset **CC BY 4.0**. The article separately carries **CC BY-NC-ND 4.0**: do not transfer the dataset license to article figures/text. No article figures, full text or original-paper graphics are bundled. The small CSV fixture preserves selected dataset field strings and carries attribution plus the original one-based data-row indices. This selection is a disclosed subset; it is not a new dataset of experiments. Full data are retrieved into ignored `.local/` by setup. Original studies have not each been independently re-read; their citations are dataset-supplied provenance.

## Schema inspection

The exact field list, inferred numeric/text types, missingness and categorical counts are in `artifacts/dataset_inspection.json`, generated from the pinned full CSV. Numeric inference is a parser observation, not a unit declaration. Key fields:

- `Reference`, `DOI`, `Year`, `Class`, `Formula`; `Parsed_Formula_*`, `Delta_O`.
- `Ea`, `A`: complete in all 483 rows; article Table 1 establishes units.
- `EaHT`, `AHT`: absent in 368 rows; present in 115. `T*`: absent in 374 rows.
- Six rows have HT values without `T*`: **66, 68, 72, 462, 463, 464** (one-based data row, header excluded). First three contain EaHT=0 and AHT=1. These are not silently interpreted as a valid regime or missing-value sentinel.
- `Type_of_conductivity`: bulk 156; total 153; `(not clearly mentioned, probably total)` 174. The last category remains unknown.
- `Measurement_temperature_range`: every inspected string explicitly uses K. 82 distinct strings; parser accepts only validated finite increasing ranges.
- `Measurement`, `Source`, `Plot type` preserve experimental technique and source table/figure location. Original plot type does not override the dataset's curated parameter convention.
- 21 distinct raw class labels; do not silently collapse to the paper's 14 broader classes.
- No per-record uncertainty/covariance, atmosphere, density or preparation columns. Absence is not evidence of matching conditions.

The fallback arXiv v2 HTML endpoint returned 404; no claims rely on it. Public event evidence is recorded separately in `COMPETITION_RULES.md`.
