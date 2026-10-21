import csv
import hashlib
import io
import json

import pytest

from backend.app.data.ingest import (
    DATASET_SHA256,
    FIXTURE_DIR,
    FULL_PATH,
    DataError,
    Repository,
    parse_csv,
)


def test_published_fixture_preserves_identity(repo):
    assert len(repo.records) == 24
    assert repo.by_id[1].raw["Ea"] == "772"
    assert repo.by_id[1].source_doi == "10.1111/j.1151-2916.1998.tb02662.x"
    assert repo.source.license == "CC-BY-4.0"
    assert repo.source.dataset_sha256 == DATASET_SHA256
    assert len(repo.by_id[1].raw) == 34


def test_fixture_checksum_and_exact_column_schema():
    manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text())
    content = (FIXTURE_DIR / "published_subset.csv").read_bytes()
    assert hashlib.sha256(content).hexdigest() == manifest["fixture_sha256"]
    with pytest.raises(DataError, match="SCHEMA_MISMATCH"):
        parse_csv(content, ["invented_column"], manifest["source_row_ids"])
    with pytest.raises(DataError, match="ROW_ID_MISMATCH"):
        parse_csv(content, manifest["columns"], [1])


def test_malformed_csv_is_rejected():
    manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text())
    content = (FIXTURE_DIR / "published_subset.csv").read_bytes().splitlines()
    damaged = b"\n".join([content[0], content[1] + b",EXTRA"])
    with pytest.raises(DataError, match="MALFORMED_ROW"):
        parse_csv(damaged, manifest["columns"], [1])


def test_no_unknown_type_coercion(repo):
    assert repo.by_id[66].conductivity_type == "(not clearly mentioned, probably total)"
    assert repo.by_id[66].conductivity_type != "total"


@pytest.mark.skipif(
    not FULL_PATH.exists(), reason="Full dataset not downloaded; published fixture tests still run"
)
def test_full_dataset_and_fixture_string_identity(repo):
    full = Repository()
    assert full.source.row_count == 483
    assert len({r.source_doi for r in full.records}) == 84
    assert len({r.formula for r in full.records}) == 452
    assert all(full.by_id[r.row_id].raw == r.raw for r in repo.records)


def test_missing_identity_rejected():
    manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text())
    columns = manifest["columns"]
    rows = list(csv.DictReader(io.StringIO((FIXTURE_DIR / "published_subset.csv").read_text())))
    rows[0]["DOI"] = ""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns)
    writer.writeheader()
    writer.writerow(rows[0])
    with pytest.raises(DataError, match="MISSING_IDENTITY"):
        parse_csv(out.getvalue().encode(), columns, [1])


def test_missing_full_file_explicitly_labels_fixture(monkeypatch, tmp_path):
    import backend.app.data.ingest as module

    monkeypatch.setattr(module, "FULL_PATH", tmp_path / "absent.csv")
    result = module.Repository()
    assert result.source.scope == "REAL_PUBLISHED_FIXTURE"
    assert result.source.row_count == 24
    assert result.source.loaded_sha256 != result.source.dataset_sha256


def test_corrupt_full_file_never_silently_uses_fixture(monkeypatch, tmp_path):
    import backend.app.data.ingest as module

    path = tmp_path / "corrupt.csv"
    path.write_bytes(b"invalid published data")
    monkeypatch.setattr(module, "FULL_PATH", path)
    with pytest.raises(DataError, match="CHECKSUM_MISMATCH"):
        module.Repository()
