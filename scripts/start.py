"""One-command local startup. --offline skips package installs/builds/downloads."""

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("uv is required; install it first (see README)")
    if not args.offline:
        run([uv, "sync", "--locked", "--link-mode", "copy"])
        try:
            run([uv, "run", "--no-sync", "python", "scripts/fetch_data.py"])
        except subprocess.CalledProcessError:
            if (ROOT / ".local/datasets/oxygen_ion_conductor_dataset.csv").exists():
                raise SystemExit(
                    "Cached full data failed verification; no silent fallback. Inspect or re-fetch with --force."
                ) from None
            print(
                "Full data fetch failed; continuing with explicitly labelled real published subset."
            )
        npm = shutil.which("npm")
        if not npm:
            raise SystemExit("npm is required to build the dashboard; see README")
        run([npm, "ci", "--prefix", "frontend", "--no-fund", "--no-audit"])
        run([npm, "run", "build", "--prefix", "frontend"])
    if not (ROOT / "frontend/dist/index.html").exists():
        raise SystemExit(
            "Dashboard not built; run python scripts/start.py once with network available"
        )
    print("OxyProof local demo: http://127.0.0.1:8000 (Ctrl+C stops)", flush=True)
    run(
        [
            uv,
            "run",
            "--offline",
            "--no-sync",
            "python",
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]
    )


if __name__ == "__main__":
    main()
