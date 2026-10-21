"""Install optional Chromium locally on D: and run genuine browser/API tests."""

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--record", action="store_true", help="Capture the separate captioned demo")
    args = parser.parse_args()
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(ROOT / ".local/ms-playwright"))
    # Real model acceptance uses the explicitly authorized CLI, never this regression suite.
    env.pop("OPENAI_API_KEY", None)
    env.pop("DEEPSEEK_API_KEY", None)
    env["OXYPROOF_DISABLE_CLOUD"] = "1"
    env.pop("OXYPROOF_LLM_MODEL", None)
    env["OXYPROOF_LLM_PROVIDER"] = "openai"
    env.pop("OXYPROOF_OLLAMA_BASE_URL", None)
    cli = ROOT / "frontend/node_modules/playwright/cli.js"
    if args.install:
        subprocess.run(["node", str(cli), "install", "chromium"], env=env, check=True, timeout=300)
    command = ["node", str(cli), "test"]
    if args.record:
        command.extend(["--config", "demo.config.ts"])
    raise SystemExit(
        subprocess.run(command, cwd=ROOT / "frontend", env=env, timeout=300).returncode
    )
