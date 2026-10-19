import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import Repository  # noqa: E402
from backend.app.reports.audit import screen  # noqa: E402
from backend.app.schemas import ScreenRequest  # noqa: E402

CASES = {
    "600c_huang_bulk": ScreenRequest(row_ids=[1, 2, 3]),
    "827c_cobalt_bulk": ScreenRequest(goal="Screen bulk conductivity at 1100 K", row_ids=[39]),
    "327c_bismuth_bulk": ScreenRequest(goal="Screen bulk conductivity at 600 K", row_ids=[483]),
    "ambiguous_regime": ScreenRequest(row_ids=[462]),
    "out_of_range": ScreenRequest(row_ids=[39]),
}


def main() -> None:
    # Always use the portable real subset, even if full data is present.
    repo = Repository(fixture_only=True)
    output = ROOT / "artifacts"
    output.mkdir(exist_ok=True)
    for name, request in CASES.items():
        result = screen(request, repo)
        (output / f"{name}.json").write_text(
            result.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        expected = (
            "INSUFFICIENT_EVIDENCE"
            if name in ("ambiguous_regime", "out_of_range")
            else "CALCULATED_WITH_WARNINGS"
        )
        if result.status != expected:
            raise SystemExit(f"DEMO_FAILED {name}: {result.status}")
        print(
            json.dumps(
                {
                    "case": name,
                    "status": result.status,
                    "candidates": len(result.candidates),
                    "excluded": len(result.excluded),
                    "mode": result.runtime_mode,
                }
            )
        )
    print("OFFLINE_DEMO=PASS cases=5 real_published_fixture=true network_calls=0")


if __name__ == "__main__":
    main()
