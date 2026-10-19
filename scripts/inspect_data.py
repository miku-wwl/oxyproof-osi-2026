"""Reproducible schema/missingness inspection, not statistical uncertainty."""

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import FULL_PATH, Repository  # noqa: E402


def main() -> None:
    repo = Repository()
    if repo.source.scope != "FULL_DATASET":
        raise SystemExit("FULL_DATASET_REQUIRED: run scripts/fetch_data.py")
    frame = pd.read_csv(FULL_PATH)
    report = {
        "source": repo.source.model_dump(),
        "bytes": FULL_PATH.stat().st_size,
        "md5": hashlib.md5(FULL_PATH.read_bytes(), usedforsecurity=False).hexdigest(),
        "rows": len(frame),
        "columns": [
            {
                "name": c,
                "inferred_dtype": str(frame[c].dtype),
                "missing": int(frame[c].isna().sum()),
                "distinct_nonmissing": int(frame[c].nunique()),
            }
            for c in frame.columns
        ],
        "categorical_counts": {
            c: {str(k): int(v) for k, v in frame[c].value_counts().sort_index().items()}
            for c in ["Class", "Type_of_conductivity", "Measurement", "Plot type"]
        },
        "incomplete_ht_rows": [
            r.row_id
            for r in repo.records
            if any(r.raw[k] for k in ["EaHT", "AHT", "T*"])
            and not all(r.raw[k] for k in ["EaHT", "AHT", "T*"])
        ],
        "not_present": [
            "parameter_uncertainty",
            "parameter_covariance",
            "atmosphere",
            "preparation",
            "sample_density",
        ],
    }
    output = ROOT / "artifacts/dataset_inspection.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"INSPECTED_REAL rows={len(frame)} columns={len(frame.columns)} source_dois={frame.DOI.nunique()}"
    )


if __name__ == "__main__":
    main()
