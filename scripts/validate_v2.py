"""Run the recorded local acceptance commands sequentially, without external model calls."""

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    parser.add_argument(
        "--phase26",
        action="store_true",
        help="Write separate Phase 2.6 evidence and run agent acceptance",
    )
    parser.add_argument(
        "--phase261",
        action="store_true",
        help="Separate Ollama sprint regression evidence; never activates inference",
    )
    parser.add_argument(
        "--phase262", action="store_true", help="DeepSeek sprint regression; no cloud/model calls"
    )
    args = parser.parse_args()
    logs = ROOT / (
        ".local/validation-deepseek"
        if args.phase262
        else ".local/validation-ollama"
        if args.phase261
        else ".local/validation-agent"
        if args.phase26
        else ".local/validation-v2"
    )
    logs.mkdir(parents=True, exist_ok=True)
    npm = Path(shutil.which("npm") or "npm").resolve()
    npm_cli = (
        npm.parent / "node_modules/npm/bin/npm-cli.js"
        if npm.suffix.lower() in (".cmd", ".ps1", ".exe")
        else npm
    )
    commands = [
        ("lock", ["uv", "lock", "--check", "--offline"]),
        (
            "backend_lint",
            [
                "uv",
                "run",
                "--offline",
                "--no-sync",
                "python",
                "-m",
                "ruff",
                "check",
                "backend",
                "scripts",
                "tests",
                "benchmarks",
            ],
        ),
        (
            "backend_format",
            [
                "uv",
                "run",
                "--offline",
                "--no-sync",
                "python",
                "-m",
                "ruff",
                "format",
                "--check",
                "backend",
                "scripts",
                "tests",
                "benchmarks",
            ],
        ),
        ("pytest", ["uv", "run", "--offline", "--no-sync", "python", "-m", "pytest", "-q"]),
        *[
            (name, ["node", str(npm_cli), "run", script, "--prefix", "frontend"])
            for name, script in [
                ("frontend_build", "build"),
                ("frontend_lint", "lint"),
                ("frontend_components", "test"),
            ]
        ],
        *[
            (name, ["uv", "run", "--offline", "--no-sync", "python", script])
            for name, script in [
                ("reference_values", "scripts/reference_values.py"),
                ("legacy_demo", "scripts/demo.py"),
                ("legacy_guards", "benchmarks/evaluate.py"),
                ("scientific_benchmark", "benchmarks/evaluate_v2.py"),
                ("phase2_demo", "scripts/phase2_demo.py"),
                ("data_inspection", "scripts/inspect_data.py"),
            ]
        ],
    ]
    if args.browser:
        commands.append(
            (
                "browser_e2e",
                ["uv", "run", "--offline", "--no-sync", "python", "scripts/browser_e2e.py"],
            )
        )
    if args.phase26 or args.phase261 or args.phase262:
        commands.extend(
            [
                (
                    "agent_acceptance",
                    [
                        "uv",
                        "run",
                        "--offline",
                        "--no-sync",
                        "python",
                        "scripts/accept_real_agent.py",
                    ],
                ),
                (
                    "independent_science",
                    [
                        "uv",
                        "run",
                        "--offline",
                        "--no-sync",
                        "python",
                        "scripts/verify_final_science.py",
                    ],
                ),
            ]
        )
    results = []
    regression_env = dict(os.environ)
    for name in (
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "OXYPROOF_LLM_MODEL",
        "OXYPROOF_OLLAMA_BASE_URL",
    ):
        regression_env.pop(name, None)
    regression_env.update(OXYPROOF_LLM_PROVIDER="openai", OXYPROOF_DISABLE_CLOUD="1")
    for name, command in commands:
        started = time.monotonic()
        try:
            process = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
                env=regression_env,
            )
            output = process.stdout + process.stderr
            code = process.returncode
        except (OSError, subprocess.SubprocessError) as exc:
            code, output = 1, str(exc)
        (logs / (name + ".txt")).write_text(output, encoding="utf-8")
        results.append(
            {
                "name": name,
                "command": command,
                "exit_code": code,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "log_path": (logs / (name + ".txt")).relative_to(ROOT).as_posix(),
                "output": output,
            }
        )
        print(f"{name}: {'PASS' if code == 0 else 'FAIL'}", flush=True)
    result = {
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "status": "PASS" if all(r["exit_code"] == 0 for r in results) else "FAIL",
        "checks": results,
        "note": "Local Windows execution; no live model, external deployment or statistically representative benchmark.",
    }
    (
        ROOT
        / (
            "artifacts/deepseek_regression.json"
            if args.phase262
            else "artifacts/ollama_regression.json"
            if args.phase261
            else "artifacts/real_agent_validation.json"
            if args.phase26
            else "artifacts/phase2_validation.json"
        )
    ).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PHASE2_VALIDATION=" + result["status"])
    raise SystemExit(result["status"] != "PASS")
