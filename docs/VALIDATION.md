# Executed validation — 2026-10-20 NZDT

This is local Windows evidence, not production/cloud/browser evidence. Runtime: uv-managed CPython **3.12.13**, uv **0.11.16**, Node **26.5.0**, npm **12.0.1**; Vite **7.3.7**, Vitest **4.1.12**. Dependencies pinned in `uv.lock` and `frontend/package-lock.json`.

| Command / check | Actual result | Boundary |
| --- | --- | --- |
| `uv sync --locked --link-mode copy` | PASS, 31 resolved / 30 packages checked | Current local environment |
| `uv lock --check --offline` | PASS, 31 packages resolved | Lockfile consistency |
| `uv run --offline --no-sync python -m pytest -q` | **94 passed, 1 warning in 3.51s** | No live LLM; full-file/fixture equality check ran, no skipped tests |
| `uv run --offline --no-sync python -m ruff check backend scripts tests benchmarks` | **All checks passed!** | Backend/scripts/tests/benchmark lint |
| `uv run --offline --no-sync python -m ruff format --check backend scripts tests benchmarks` | **29 files already formatted** | Final benchmark edit was formatted separately |
| `npm run build --prefix frontend` | **1581 modules transformed; built in 4.72s** | TypeScript and production bundle; not visual browser acceptance |
| `npm run lint --prefix frontend` | PASS, exit 0, no errors/warnings | ESLint, `--max-warnings 0` |
| `npm run test --prefix frontend` | **1 test file passed; 6 tests passed** | DOM/component contracts with mocked HTTP, not browser E2E |
| `npm audit --prefix frontend --registry=https://registry.npmjs.org --json` | **0 vulnerabilities** | Registry snapshot at inspection, not a security guarantee |
| `uv run --offline --no-sync python scripts/reference_values.py` | **4 reference calculations**, production agreement rel. 2e-14 tested | Independent 60-digit Decimal/SI arithmetic |
| `uv run --offline --no-sync python scripts/demo.py` | **OFFLINE_DEMO=PASS cases=5** | 3 normal real-data cases + 2 explicit abstentions; portable published fixture |
| `uv run --offline --no-sync python benchmarks/evaluate.py` | **MEASURED guard_cases=8 baseline_correct=1 audited_correct=8** | Fixed educational guard corpus, no general accuracy claim |
| `uv run --offline --no-sync python scripts/inspect_data.py` | **INSPECTED_REAL rows=483 columns=34 source_dois=84** | Dataset schema/metadata, not experimental replication |
| `python scripts/start.py --offline` | PASS; HTTP server reached ready state | No package sync/build/data download |
| `python scripts/start.py` | PASS; locked sync → cached CSV verification → clean `npm ci` → build → ready server | Current-machine bootstrap; initial empty-machine setup not separately replicated |
| `uv run --offline --no-sync python scripts/smoke.py` | **HTTP_SMOKE=PASS checks=6 scope=FULL_DATASET** | Genuine localhost HTTP to separately running server; see `artifacts/http_smoke.json` |
| Full default 600 °C API calculation | 483 matched; 20 provisional groups; 71 shown; 363 excluded/unranked | Top 5 per group; another 49 eligible in-group tail entries omitted, not globally ranked |
| Five deterministic audit artifacts | PASS: Pydantic contract, raw fields equal fixture, current code fingerprint | JSON outputs under artifacts; no hand-authored scientific values |
| Browser E2E / visible page / download interaction | **NOT RUN** | CUA returned `Browser is not available: iab`, inventory `apps: [], browsers: []` |
| Live `REAL_LLM` | **NOT_CONFIGURED** | No API credential detected; mocked adapter tests only |
| POSIX runtime / public deployment | **NOT RUN** | Commands supplied, not executed on POSIX; no deployment authorized |

After adding baseline numeric traces, its focused regression check also ran: `uv run --offline --no-sync python -m pytest -q tests/test_workflow.py::test_measured_guard_benchmark` → **1 passed, 1 warning in 0.57s**. This is one of the 94 existing tests, not an extra distinct test. Benchmark was then re-executed and its measured counts stayed 1/8 vs 8/8.

The retained warning is Starlette's TestClient deprecation of the current httpx bridge. It does not invalidate the real urllib localhost smoke. A future test-client migration should be deliberate; no warning has been hidden.

## Errors encountered and resolved

- Nature's web reader hit a cookie-redirect 500; direct Python HTTPS retrieval of the article and Table 1 succeeded. A guessed arXiv v2 HTML endpoint returned 404; no claims rely on it. The event `/faq/` path returned 404; eligibility basics were read from the homepage FAQ.
- Initial uv installation hit `Failed to update Windows PE resources ... uv-trampoline ... Access denied`. A later locked sync succeeded. Validation uses `uv run python -m ...` to bind the intended venv, rather than risk a global test executable. An early collection error used pytest's reserved name `request`; it was fixed before the complete passing runs.
- Initial frontend run found one Hook cleanup lint warning and one ambiguous test selector. Both were fixed; final build/lint/tests passed. One premature lint/test attempt overlapped bootstrap's `npm ci` and found removed command shims; rerunning sequentially after installation passed.
- npm's mirror audit endpoint returned `404 [NOT_IMPLEMENTED]`; official-registry audit worked. The initial Vitest dependency had advisories, so it was upgraded to a patched 4.1.x release; audit then returned zero. No automatic broad `audit fix` was used.
- Clean install against old mirror tarball URLs failed `EALLOWREMOTE: Fetching packages of type remote have been disabled`. Lockfile URLs were normalized to official npm registry with versions and integrity hashes unchanged. `npm ci` and full bootstrap then passed. Only project-local registry configuration was added; no global npm settings changed.
- npm reports esbuild's postinstall blocked by local allowScripts policy. The installed platform binary supports the actual successful builds. No security setting was weakened or bypassed.
- A nonfinite JSON probe exposed a 500 during validation-error serialization. A bounded error handler now returns 422 without echoing invalid values. NaN and ±Infinity regression tests pass.

No outstanding automated test failure is known. Browser behavior, live model availability, original-study measurement conditions and organizer-specific submission requirements remain unverified.
