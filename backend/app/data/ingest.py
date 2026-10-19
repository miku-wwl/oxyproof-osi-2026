"""Pinned, attributed published data. No request-supplied file path or URL."""

import csv
import hashlib
import io
import json
from pathlib import Path

from backend.app.schemas import Record, SourceInfo

ROOT = Path(__file__).resolve().parents[3]
DATASET_SHA256 = "8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34"
DATASET_MD5 = "45f25ce4ef0240271ee5c35ea75400f1"
DATASET_DOI = "10.5281/zenodo.18947543"
DATA_URL = "https://zenodo.org/records/18947543/files/oxygen_ion_conductor_dataset.csv?download=1"
FULL_PATH = ROOT / ".local/datasets/oxygen_ion_conductor_dataset.csv"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


class DataError(ValueError):
    pass


def parse_csv(content: bytes, columns: list[str], row_ids: list[int]) -> list[Record]:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=""))
    if reader.fieldnames != columns:
        raise DataError("SCHEMA_MISMATCH: exact published column sequence required")
    rows = list(reader)
    if len(rows) != len(row_ids) or len(set(row_ids)) != len(row_ids):
        raise DataError("ROW_ID_MISMATCH")
    result = []
    for row_id, raw in zip(row_ids, rows, strict=True):
        if None in raw or any(v is None for v in raw.values()):
            raise DataError(f"MALFORMED_ROW: {row_id}")
        if not all(raw[k].strip() for k in ["Formula", "DOI", "Reference"]):
            raise DataError(f"MISSING_IDENTITY: {row_id}")
        if not raw["DOI"].startswith("10.") or any(c.isspace() for c in raw["DOI"]):
            raise DataError(f"INVALID_SOURCE_DOI: {row_id}")
        result.append(
            Record(
                row_id=row_id,
                formula=raw["Formula"],
                material_class=raw["Class"],
                source_doi=raw["DOI"],
                reference=raw["Reference"],
                conductivity_type=raw["Type_of_conductivity"],
                measurement=raw["Measurement"],
                temperature_range_raw=raw["Measurement_temperature_range"],
                raw=raw,
            )
        )
    return result


class Repository:
    def __init__(self, *, fixture_only: bool = False):
        manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text(encoding="utf-8"))
        full = FULL_PATH.exists() and not fixture_only
        path = FULL_PATH if full else FIXTURE_DIR / "published_subset.csv"
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        expected = DATASET_SHA256 if full else manifest["fixture_sha256"]
        if digest != expected:
            # Never silently fall back from a tampered full file to the fixture.
            raise DataError("CHECKSUM_MISMATCH: rerun scripts/fetch_data.py")
        ids = list(range(1, 484)) if full else manifest["source_row_ids"]
        self.records = parse_csv(content, manifest["columns"], ids)
        self.by_id = {r.row_id: r for r in self.records}
        self.source = SourceInfo(
            dataset_doi=DATASET_DOI,
            dataset_record_id="18947543",
            dataset_sha256=DATASET_SHA256,
            loaded_sha256=digest,
            scope="FULL_DATASET" if full else "REAL_PUBLISHED_FIXTURE",
            row_count=len(self.records),
            license="CC-BY-4.0",
            accessed_date="2026-10-20",
            article_url="https://www.nature.com/articles/s41597-026-07100-x",
            dataset_url="https://zenodo.org/records/18947543",
            attribution=manifest["attribution"],
        )

    def classes(self) -> list[str]:
        return sorted({r.material_class for r in self.records})
