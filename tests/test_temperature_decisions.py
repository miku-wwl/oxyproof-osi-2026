import copy
import math
from decimal import Decimal, localcontext

import pytest

from backend.app.agents.workflow import run_research
from backend.app.schemas import Record
from backend.app.science.decision_schemas import AgentRequest, TemperatureRequest
from backend.app.science.temperature_decisions import analyze_temperature_interval


def reference(raw, temperature, suffix):
    # Independent SI/Decimal reference; no production math or regime selector.
    with localcontext() as ctx:
        ctx.prec = 60
        t = Decimal(str(temperature))
        ea_j = Decimal(raw["Ea" + suffix]) * Decimal("0.001") * Decimal("1.602176634e-19")
        return float(Decimal(raw["A" + suffix]) / t * (-ea_j / (Decimal("1.380649e-23") * t)).exp())


def test_real_flagship_independent_ordering_and_math(repo):
    report = analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2, 3], selected_temperatures=[700, 1000]), repo
    )
    assert report.status == "CALCULATED_WITH_WARNINGS"
    assert [p.ordering for p in report.selected_rankings] == [[1, 2, 3], [3, 2, 1]]
    for p, suffix in zip(report.selected_rankings, ["", "HT"], strict=True):
        for value in p.values:
            assert value.conductivity_s_cm == pytest.approx(
                reference(repo.by_id[value.row_id].raw, p.temperature_k, suffix), rel=2e-14
            )
    assert {m.record.source_doi for m in report.materials} == {"10.1111/j.1151-2916.1998.tb02662.x"}
    assert all(m.measured_range_k == [600, 1100] for m in report.materials)
    assert (
        len(
            [
                e
                for e in report.events
                if e.kind == "PUBLISHED_REGIME_BOUNDARY"
                or e.kind == "REGIME_BOUNDARY_DRIVEN_CHANGE"
            ]
        )
        == 3
    )
    for event in report.events:
        if event.exact_continuous_crossing:
            left, right = [repo.by_id[i] for i in event.row_ids]
            for record in [left, right]:
                assert abs(event.temperature_k - float(record.raw["T*"])) > 1e-6
            a = reference(
                left.raw,
                event.temperature_k,
                "HT" if event.temperature_k > float(left.raw["T*"]) else "",
            )
            b = reference(
                right.raw,
                event.temperature_k,
                "HT" if event.temperature_k > float(right.raw["T*"]) else "",
            )
            assert a == pytest.approx(b, rel=2e-13)


def test_resolution_independence_and_determinism(repo):
    coarse = analyze_temperature_interval(TemperatureRequest(row_ids=[1, 2, 3], points=2), repo)
    fine = analyze_temperature_interval(TemperatureRequest(row_ids=[1, 2, 3], points=201), repo)
    assert coarse.events == fine.events and coarse.segments == fine.segments
    assert coarse == analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2, 3], points=2), repo
    )


def test_kelvin_celsius_interval_equivalence(repo):
    k = analyze_temperature_interval(TemperatureRequest(row_ids=[1, 2, 3]), repo)
    c = analyze_temperature_interval(
        TemperatureRequest(
            row_ids=[1, 2, 3], temperature_min=326.85, temperature_max=826.85, temperature_unit="C"
        ),
        repo,
    )
    assert k.events == c.events
    assert k.segments == c.segments


def synthetic_repo(repo, *, discontinuity=False, outside=False):
    # SYNTHETIC_TEST_ONLY analytically designed fits, never product demo data.
    repository = copy.copy(repo)
    records = []
    kb = 1.380649e-23 / 1.602176634e-19
    for row in [1, 2]:
        record = repo.by_id[row].model_copy(deep=True)
        record.formula = "SYNTHETIC_TEST_ONLY_" + str(row)
        record.raw.update(
            Formula=record.formula, Ea="500", A="100000", EaHT="", AHT="", **{"T*": ""}
        )
        if row == 2:
            if discontinuity:
                record.raw.update(A="50000", EaHT="500", AHT="200000", **{"T*": "800"})
            else:
                root = 1400 if outside else 800
                record.raw.update(Ea="600", A=str(100000 * math.exp(0.1 / (kb * root))))
        records.append(Record.model_validate(record.model_dump()))
    repository.records = records
    repository.by_id = {r.row_id: r for r in records}
    return repository


def test_analytic_known_continuous_root(repo):
    report = analyze_temperature_interval(TemperatureRequest(row_ids=[1, 2]), synthetic_repo(repo))
    roots = [e for e in report.events if e.exact_continuous_crossing]
    assert len(roots) == 1 and roots[0].temperature_k == pytest.approx(800, abs=1e-10)


def test_discontinuity_never_mislabeled_continuous(repo):
    report = analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2]), synthetic_repo(repo, discontinuity=True)
    )
    assert not any(e.exact_continuous_crossing for e in report.events)
    event = next(e for e in report.events if e.kind == "REGIME_BOUNDARY_DRIVEN_CHANGE")
    assert event.temperature_k == 800
    assert event.left_ordering == [1, 2] and event.right_ordering == [2, 1]
    point = next(p for p in report.boundary_rankings if p.temperature_k == 800)
    assert not point.ordering and any("AT_TRANSITION" in x.reasons for x in point.excluded)


def test_root_outside_joint_evidence_rejected(repo):
    report = analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2]), synthetic_repo(repo, outside=True)
    )
    assert not report.events
    assert report.rejected_crossovers[0].candidate_temperature_k == pytest.approx(1400)


def test_identical_model_ties_are_not_strict_winner_claims(repo):
    synthetic = synthetic_repo(repo)
    synthetic.by_id[2].raw.update(Ea="500", A="100000")
    report = analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2], selected_temperatures=[700]), synthetic
    )
    assert report.selected_rankings[0].values[0].tie_with == [2]
    assert report.segments[0].tie_groups == [[1, 2]]
    assert "1 = 2" in report.interpretation[0]
    assert not any(e.exact_continuous_crossing for e in report.events)


def test_interval_analysis_has_no_network_dependency(repo, monkeypatch):
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("Offline interval analysis attempted network access")

    monkeypatch.setattr(socket, "socket", forbidden)
    report = analyze_temperature_interval(TemperatureRequest(row_ids=[1, 2, 3]), repo)
    assert report.status == "CALCULATED_WITH_WARNINGS"


def test_no_ranking_outside_range_or_at_tstar(repo):
    report = analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2, 3], temperature_min=500, temperature_max=1200), repo
    )
    for p in report.curve_points:
        if p.temperature_k < 600 or p.temperature_k > 1100:
            assert not p.ordering and not p.values
        for v in p.values:
            assert abs(p.temperature_k - float(repo.by_id[v.row_id].raw["T*"])) > 1e-6


@pytest.mark.parametrize(
    "kwargs,reason",
    [
        ({"row_ids": [1, 39]}, "NON_COMPARABLE_SOURCE_GROUPS"),
        ({"row_ids": [1]}, "INSUFFICIENT_EVIDENCE"),
        ({"row_ids": [1, 2, 3], "conductivity_type": "total"}, "INSUFFICIENT_EVIDENCE"),
        (
            {
                "row_ids": [1, 2, 3],
                "goal": "Compare bulk conductors between 600 K and 1100 K in wet air",
            },
            "UNVERIFIED_CONSTRAINTS",
        ),
        ({"row_ids": [1, 2, 3], "temperature_min": 1200}, "INVALID_INTERVAL"),
    ],
)
def test_interval_refusals(repo, kwargs, reason):
    result = analyze_temperature_interval(TemperatureRequest(**kwargs), repo)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert reason in result.evidence_verdicts


def test_temperature_api_and_agent(client, repo):
    result = client.post(
        "/api/temperature-decisions",
        json={"row_ids": [1, 2, 3], "selected_temperatures": [700, 1000]},
    ).json()
    assert result["selected_rankings"][0]["ordering"] == [1, 2, 3]
    assert (
        client.post(
            "/api/temperature-decisions", json={"row_ids": [1, 2, 3], "mode": "REAL_LLM"}
        ).status_code
        == 503
    )
    assert (
        client.post(
            "/api/temperature-decisions", json={"row_ids": [1, 2, 3], "temperature_unit": "F"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/temperature-decisions",
            json={"row_ids": [1, 2, 3], "evidence_policy": "ALLOW_ANY"},
        ).status_code
        == 422
    )
    for goal, tool in [
        ("Find bulk conductors at 600 C", "screen_published_records"),
        ("Compare bulk conductors between 600 K and 1100 K", "analyze_temperature_interval"),
        ("Inspect scientific evidence row 1", "inspect_scientific_evidence"),
    ]:
        response = run_research(AgentRequest(goal=goal, row_ids=[1, 2, 3]), repo)
        assert response["tool_name"] == tool
        assert (
            response["result"].status != "UNAVAILABLE"
            if hasattr(response["result"], "status")
            else response["result"]["record"].row_id == 1
        )
