"""Download only a fixed, inspected public resource; verify before replacing cache."""

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.data.ingest import (  # noqa: E402
    DATA_URL,
    DATASET_MD5,
    DATASET_SHA256,
    FIXTURE_DIR,
    FULL_PATH,
    parse_csv,
)


def validate(data: bytes) -> None:
    if len(data) != 122657:
        raise ValueError(f"SIZE_MISMATCH: expected 122657, got {len(data)}")
    if hashlib.sha256(data).hexdigest() != DATASET_SHA256:
        raise ValueError("SHA256_MISMATCH")
    if hashlib.md5(data, usedforsecurity=False).hexdigest() != DATASET_MD5:
        raise ValueError("MD5_MISMATCH")
    columns = json.loads((FIXTURE_DIR / "manifest.json").read_text(encoding="utf-8"))["columns"]
    parse_csv(data, columns, list(range(1, 484)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if FULL_PATH.exists() and not args.force:
        validate(FULL_PATH.read_bytes())
        print(f"VERIFIED_CACHED {FULL_PATH} SHA256={DATASET_SHA256}")
        return
    # One attempt, 30-second timeout, hard size bound; no arbitrary URL parameter.
    request = urllib.request.Request(DATA_URL, headers={"User-Agent": "OxyProof/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(200000)
    validate(data)
    FULL_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = FULL_PATH.with_suffix(".tmp")
    temporary.write_bytes(data)
    temporary.replace(FULL_PATH)
    print(f"VERIFIED_REAL rows=483 license=CC-BY-4.0 SHA256={DATASET_SHA256}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"DATA_FETCH_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("Fallback: the attributed published subset remains usable offline.", file=sys.stderr)
        sys.exit(1)
