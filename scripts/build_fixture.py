"""Maintainer operation: extract original field strings from the pinned full data."""

import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import DATASET_SHA256, FIXTURE_DIR, FULL_PATH  # noqa: E402

ROWS = [
    1,
    2,
    3,
    39,
    40,
    66,
    68,
    72,
    79,
    135,
    152,
    190,
    220,
    280,
    300,
    350,
    400,
    450,
    462,
    463,
    464,
    470,
    480,
    483,
]


def main() -> None:
    data = FULL_PATH.read_bytes()
    if hashlib.sha256(data).hexdigest() != DATASET_SHA256:
        raise SystemExit("CHECKSUM_MISMATCH")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    columns = reader.fieldnames
    all_rows = list(reader)
    selected = [all_rows[i - 1] for i in ROWS]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(selected)
    fixture = buffer.getvalue().encode("utf-8")
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    (FIXTURE_DIR / "published_subset.csv").write_bytes(fixture)
    manifest = {
        "fixture_version": "1.0",
        "kind": "REAL_PUBLISHED_FIXTURE",
        "source_dataset_doi": "10.5281/zenodo.18947543",
        "source_dataset_sha256": DATASET_SHA256,
        "fixture_sha256": hashlib.sha256(fixture).hexdigest(),
        "source_row_id_convention": "One-based CSV data-row index, header excluded. No intrinsic material ID is provided.",
        "source_row_ids": ROWS,
        "columns": columns,
        "license": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "Jang, Seong-Hoon; Kiyohara, Shin; Takamura, Hitoshi; Kumagai, Yu (2026). Charting the Landscape of Oxygen Ion Conductors: A 60-Year Dataset. Zenodo. https://doi.org/10.5281/zenodo.18947543. CC BY 4.0.",
        "modifications": "Selected 24 records; UTF-8 encoding and LF line endings. Original field strings unchanged, no added experimental values.",
    }
    (FIXTURE_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"FIXTURE_REAL rows={len(ROWS)} SHA256={manifest['fixture_sha256']}")


if __name__ == "__main__":
    main()
