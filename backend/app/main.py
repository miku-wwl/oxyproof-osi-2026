from functools import lru_cache
from pathlib import Path
from threading import BoundedSemaphore

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.agents.llm import LLMError, configured
from backend.app.agents.workflow import run_research, run_temperature
from backend.app.data.ingest import ROOT, DataError, Repository
from backend.app.reports.audit import calculate_record, code_version, group_key, screen
from backend.app.schemas import AuditReport, ScreenRequest
from backend.app.science.conductivity import ScienceError, to_kelvin, wrong_equation_demo
from backend.app.science.decision_schemas import (
    AgentExecution,
    AgentRequest,
    TemperatureReport,
    TemperatureRequest,
)

app = FastAPI(
    title="OxyProof",
    version="0.1.0",
    description="Published-data screening; conditional group ranks; explicit abstention.",
)
llm_lock = BoundedSemaphore(1)


@app.exception_handler(RequestValidationError)
async def request_validation_error(_request, exc: RequestValidationError):
    # Do not echo invalid JSON NaN/Infinity (not JSON-serializable), secrets or raw input.
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": list(e["loc"]), "type": e["type"], "msg": e["msg"]} for e in exc.errors()
            ]
        },
    )


@lru_cache(maxsize=1)
def repository() -> Repository:
    return Repository()


def repo_or_503() -> Repository:
    try:
        return repository()
    except (OSError, ValueError, DataError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"runtime_mode": "UNAVAILABLE", "code": "DATA_UNAVAILABLE", "message": str(exc)},
        ) from exc


@app.get("/api/health")
def health():
    repo = repo_or_503()
    return {
        "status": "ok",
        "runtime_mode": "OFFLINE_DETERMINISTIC",
        "real_llm_status": "CONFIGURED_NOT_VERIFIED" if configured() else "NOT_CONFIGURED",
        "source": repo.source,
        "code_version": code_version(),
    }


@app.get("/api/catalog")
def catalog():
    repo = repo_or_503()
    return {
        "classes": repo.classes(),
        "conductivity_types": ["bulk", "total"],
        "source": repo.source,
        "comparison_groups": [
            {
                "id": key,
                "row_ids": [r.row_id for r in repo.records if group_key(r) == key],
                "source_doi": first.source_doi,
                "conductivity_type": first.conductivity_type,
                "measurement": first.measurement,
                "temperature_range": first.temperature_range_raw,
            }
            for key, first in sorted({group_key(r): r for r in repo.records}.items())
        ],
        "records": [
            {
                "row_id": r.row_id,
                "formula": r.formula,
                "class": r.material_class,
                "conductivity_type": r.conductivity_type,
                "source_doi": r.source_doi,
            }
            for r in repo.records
        ],
    }


@app.post("/api/screen", response_model=AuditReport)
def analyze(request: ScreenRequest):
    acquired = False
    if request.mode == "REAL_LLM":
        acquired = llm_lock.acquire(blocking=False)
        if not acquired:
            raise HTTPException(
                status_code=429, detail={"runtime_mode": "UNAVAILABLE", "code": "MODEL_BUSY"}
            )
    try:
        return screen(request, repo_or_503())
    except LLMError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "runtime_mode": "UNAVAILABLE",
                "code": "LLM_UNAVAILABLE",
                "message": str(exc),
                "fallback": "Select OFFLINE_DETERMINISTIC explicitly",
            },
        ) from exc
    finally:
        if acquired:
            llm_lock.release()


@app.get("/api/records/{row_id}")
def record_detail(row_id: int):
    repo = repo_or_503()
    record = repo.by_id.get(row_id)
    if not record:
        raise HTTPException(404, "ROW_NOT_LOADED")
    return {"record": record, "source": repo.source, "code_version": code_version()}


@app.post("/api/temperature-decisions", response_model=TemperatureReport)
def temperature_decisions(request: TemperatureRequest):
    return guarded_workflow(request.mode, lambda: run_temperature(request, repo_or_503()))


@app.post("/api/research", response_model=AgentExecution)
def research(request: AgentRequest):
    return guarded_workflow(request.mode, lambda: run_research(request, repo_or_503()))


def guarded_workflow(mode, operation):
    acquired = mode == "REAL_LLM" and llm_lock.acquire(blocking=False)
    if mode == "REAL_LLM" and not acquired:
        raise HTTPException(429, {"runtime_mode": "UNAVAILABLE", "code": "MODEL_BUSY"})
    try:
        return operation()
    except ScienceError as exc:
        raise HTTPException(422, {"code": exc.code, "message": str(exc)}) from exc
    except LLMError as exc:
        raise HTTPException(
            503,
            {
                "runtime_mode": "UNAVAILABLE",
                "code": "LLM_UNAVAILABLE",
                "message": str(exc),
                "fallback": "Select OFFLINE_DETERMINISTIC explicitly",
            },
        ) from exc
    finally:
        if acquired:
            llm_lock.release()


@app.get("/api/records/{row_id}/curve")
def curve(
    row_id: int,
    min_c: float = Query(300, ge=-273, le=2500),
    max_c: float = Query(1000, ge=-273, le=2500),
    points: int = Query(41, ge=2, le=101),
):
    repo = repo_or_503()
    record = repo.by_id.get(row_id)
    if not record:
        raise HTTPException(404, "ROW_NOT_LOADED")
    if max_c <= min_c:
        raise HTTPException(422, "INVALID_CURVE_RANGE")
    values = []
    for i in range(points):
        c = min_c + (max_c - min_c) * i / (points - 1)
        result = calculate_record(record, to_kelvin(c, "C"))
        quantity = result.computed_values_with_units.get("conductivity")
        values.append(
            {
                "temperature_c": c,
                "conductivity_s_cm": quantity.value if quantity else None,
                "regime": result.regime,
                "status": result.status,
                "warning_codes": [w.code for w in result.warnings],
            }
        )
    return {
        "row_id": row_id,
        "points": values,
        "source": repo.source,
        "raw_source_record": record.raw,
        "equation": "sigma(T) = A/T * exp(-Ea/(k_B*T))",
        "input_units": {
            "Ea": "meV",
            "EaHT": "meV",
            "A": "K S/cm",
            "AHT": "K S/cm",
            "T*": "K",
            "temperature_c": "C",
        },
        "output_unit": "S/cm",
        "code_version": code_version(),
        "warnings": [
            "Nulls are withheld outside measurement range or at ambiguous regimes. Do not interpolate across regime changes."
        ],
    }


@app.get("/api/records/{row_id}/adversarial")
def adversarial(row_id: int, temperature_c: float = Query(600, ge=-273, le=2500)):
    repo = repo_or_503()
    record = repo.by_id.get(row_id)
    if not record:
        raise HTTPException(404, "ROW_NOT_LOADED")
    try:
        t = to_kelvin(temperature_c, "C")
        result = calculate_record(record, t)
        if result.status != "CALCULATED":
            return JSONResponse(
                status_code=422,
                content={"status": "INSUFFICIENT_EVIDENCE", "calculation": result.model_dump()},
            )
        return {
            "demo": wrong_equation_demo(result.computed_values_with_units["conductivity"].value, t),
            "calculation": result,
            "source": repo.source,
            "code_version": code_version(),
        }
    except ScienceError as exc:
        raise HTTPException(422, {"code": exc.code, "message": str(exc)}) from exc


# Built assets are served locally by the same API origin. No catch-all can hide API errors.
DIST = ROOT / "frontend/dist"
if (DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def index():
    path: Path = DIST / "index.html"
    if not path.exists():
        return {
            "message": "Build the dashboard: npm --prefix frontend ci; npm --prefix frontend run build",
            "api_docs": "/docs",
        }
    return FileResponse(path)
