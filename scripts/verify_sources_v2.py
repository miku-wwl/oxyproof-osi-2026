"""Bounded, read-only recheck of fixed scientific/event authorities; cache stays ignored."""

import hashlib
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "agenda_2026": "https://llmhackathon.github.io/agenda/",
    "article": "https://www.nature.com/articles/s41597-026-07100-x",
    "units_table": "https://www.nature.com/articles/s41597-026-07100-x/tables/1",
    "zenodo_metadata": "https://zenodo.org/api/records/18947543",
}


def verify():
    cache = ROOT / ".local/source-v2"
    cache.mkdir(parents=True, exist_ok=True)
    result = {"accessed_at_utc": datetime.now(UTC).isoformat(), "sources": []}
    for name, url in SOURCES.items():
        item = {"name": name, "url": url}
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "OxyProof-source-verification/0.2"}
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read(5_000_001)
                if len(data) > 5_000_000:
                    raise ValueError("SOURCE_SIZE_LIMIT")
                item.update(
                    status="DIRECTLY_RETRIEVED",
                    http_status=response.status,
                    bytes=len(data),
                    sha256=hashlib.sha256(data).hexdigest(),
                )
            (cache / (name + (".json" if name == "zenodo_metadata" else ".html"))).write_bytes(data)
            if name == "zenodo_metadata":
                metadata = json.loads(data)
                item["license"] = metadata["metadata"].get("license")
                item["files"] = [
                    {"key": f["key"], "checksum": f["checksum"], "size": f["size"]}
                    for f in metadata["files"]
                ]
        except (OSError, ValueError, KeyError) as exc:
            item.update(status="FAILED", error=f"{type(exc).__name__}: {exc}")
        result["sources"].append(item)
        print(name, item["status"], item.get("error", ""), flush=True)
    (ROOT / "artifacts/source_verification_v2.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    evidence = verify()
    raise SystemExit(any(s["status"] == "FAILED" for s in evidence["sources"]))
